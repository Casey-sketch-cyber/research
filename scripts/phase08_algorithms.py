"""Independent footprint and annealing baselines; final scores use the validator."""
from copy import deepcopy
from functools import lru_cache
import itertools
import math
import time
import numpy as np
from fea.furniture.library import rectangles
from fea.households import demanded_hours
from fea.metrics import fci
from fea.solve.greedy import greedy_layout
from fea.solve.reachability import walking_masks
from fea.validate import validate_layout


def empty_layout(unit, household, grid, digest):
    return dict(unit_key=unit.unit_key,source=unit.source,nia_m2=unit.interior.area,
        furnishable_area_m2=unit.classes['furnishable'].area,household=household.name,
        strategy='S2',resolution_m=grid.resolution,items=[],service={},config_hash=digest)


def footprint(empty,grid,items,candidates,household,config):
    """Use the footprint arm alone and exhaust its scan; never call the portfolio."""
    result=greedy_layout(empty,grid,items,candidates,household,config,float('inf'),policy='footprint')
    result['algorithm']='greedy_footprint';return result


def bits(mask):
    return int.from_bytes(np.packbits(mask.reshape(-1),bitorder='little').tobytes(),'little')


class Evaluator:
    """Cache rectangles and exact walking morphology for an integer genome.

    The genome keeps one pose per physical instance and one state per variant-slot.
    Candidate generation already checks every state's static geometric constraints.
    Remaining pair collisions and fixed-service failures carry explicit penalties.
    """
    def __init__(self,grid,items,candidates,household,config,empty,settings):
        self.grid,self.items,self.candidates,self.household=grid,items,candidates,household
        self.config,self.empty,self.settings=config,empty,settings
        self.names=[name for name in sorted(items) for _ in range(items[name].max_instances) if len(candidates[name])]
        counts={};self.identities=[]
        for name in self.names:
            counts[name]=counts.get(name,0)+1;self.identities.append(name+'#'+str(counts[name]))
        self.slots=[(v,slot) for v in household.variants for slot in household.slots]
        self.targets=[bits(t) for t in grid.service_targets]
        self.width=household.overrides.get('walking_width',config['furniture']['meta']['walking_width'])
        self.ncells=grid.labels.size;self.nbytes=(self.ncells+7)//8
        self.weights=[v.frequency*slot.hours/demanded_hours(household,v.name) for v,slot in self.slots]
        self.shape_cache=lru_cache(maxsize=4096)(self._shape)
        self.reach_cache=lru_cache(maxsize=512)(self._reach)
        self.assignment_cache=lru_cache(maxsize=8192)(self._assignment)

    def _shape(self,name,pose,state):
        x,y,angle=map(int,self.candidates[name][pose]);item=self.items[name]
        body,clear,_=rectangles(item.states[state],self.grid.resolution,angle)
        def rect_bits(rect):
            dx,dy,w,h=rect;row=(1<<w)-1;nx=self.grid.labels.shape[1]
            return sum(row<<((y+dy+j)*nx+x+dx) for j in range(h))
        return rect_bits(body),sum_rectangles(clear,rect_bits)

    def _reach(self,occupied):
        packed=np.frombuffer(occupied.to_bytes(self.nbytes,'little'),dtype=np.uint8)
        mask=np.unpackbits(packed,bitorder='little')[:self.ncells].reshape(self.grid.labels.shape).astype(bool)
        return bits(walking_masks(self.grid,mask,self.width)[0])

    def _assignment(self,k,available):
        variant,slot=self.slots[k];demands=variant.demand[slot.name]
        tokens={i:self.items[self.names[i]].states[state].serves for i,state in available}
        options=[]
        for demand in demands:
            choices=[(0,(),0.)]
            if demand.need=='storage':
                ids=[i for i,t in tokens.items() if 'storage' in t]
                for count in range(1,len(ids)+1):
                    for group in itertools.combinations(ids,count):
                        credit=min(1.,sum(self.items[self.names[i]].storage_units for i in group)/demand.units)
                        choices.append((sum(1<<i for i in group),group,credit))
            else:
                for rule in self.household.capability_rules[demand.need]['satisfied_by']:
                    for group in itertools.product(*[[i for i,t in tokens.items() if token in t] for token in rule]):
                        if len(group)==len(set(group)):choices.append((sum(1<<i for i in group),group,1.))
            options.append(choices)
        best=-1.;winner=[]
        for combination in itertools.product(*options):
            used=0;value=0.;valid=True
            for demand,(mask,group,credit) in zip(demands,combination):
                if used&mask:valid=False;break
                used|=mask;value+=demand.weight*credit
            if valid and value>best:best=value;winner=combination
        return best,tuple((d.id,tuple(self.identities[i] for i in group),credit,d.need) for d,(_,group,credit) in zip(demands,winner))

    def evaluate(self,genome,materialize=False):
        active=[i for i in range(len(self.names)) if genome[i,0]>=0]
        violations=0;score=0.;service={v.name:{} for v in self.household.variants}
        for k,(variant,slot) in enumerate(self.slots):
            shapes=[(i,*self.shape_cache(self.names[i],int(genome[i,0]),int(genome[i,k+1]))) for i in active]
            occupied=0;collisions=0
            for index,(identity,body,clear) in enumerate(shapes):
                occupied|=body
                for _,b,c in shapes[:index]:
                    collisions+=bool(body&b)+bool(body&c)+bool(clear&b)
            reached=self.reach_cache(occupied)
            violations+=collisions+sum(not(target&reached) for target in self.targets)
            available=tuple((i,int(genome[i,k+1])) for i,body,clear in shapes if clear&reached)
            value,assignments=self.assignment_cache(k,available);score+=self.weights[k]*value
            if materialize:service[variant.name][slot.name]=[dict(demand_id=d,by=list(ids),need=need) for d,ids,credit,need in assignments]
        burden=0.;nslots=len(self.household.slots)
        for i in active:
            for vindex,variant in enumerate(self.household.variants):
                states=genome[i,1+vindex*nslots:1+(vindex+1)*nslots]
                burden+=variant.frequency*self.items[self.names[i]].effort*int(np.sum(states!=np.roll(states,1)))
        cost=-score+self.settings['violation_penalty']*violations+self.settings['burden_weight']*burden
        result=dict(fci=float(score),tb=float(burden),violations=int(violations),cost=float(cost))
        if materialize:
            layout=deepcopy(self.empty);layout['service']=service
            for i in active:
                name=self.names[i];x,y,angle=map(int,self.candidates[name][genome[i,0]])
                states={v.name:{slot.name:self.items[name].states[int(genome[i,k+1])].name for k,(vv,slot) in enumerate(self.slots) if vv.name==v.name} for v in self.household.variants}
                layout['items'].append(dict(instance_id=self.identities[i],type=name,x=round(self.grid.origin[0]+x*self.grid.resolution,9),
                    y=round(self.grid.origin[1]+y*self.grid.resolution,9),orientation_deg=angle,states=states))
            result['layout']=layout
        return result

    def encode(self,layout):
        genome=np.zeros((len(self.names),1+len(self.slots)),dtype=np.int32);genome[:,0]=-1
        for placed in layout['items']:
            i=self.identities.index(placed['instance_id']);name=self.names[i]
            pose=[round((placed['x']-self.grid.origin[0])/self.grid.resolution),round((placed['y']-self.grid.origin[1])/self.grid.resolution),placed['orientation_deg']]
            indices=np.flatnonzero(np.all(self.candidates[name]==pose,axis=1))
            if len(indices)!=1:raise ValueError('Greedy pose is outside shared B candidates')
            genome[i,0]=indices[0]
            for k,(variant,slot) in enumerate(self.slots):genome[i,k+1]=[s.name for s in self.items[name].states].index(placed['states'][variant.name][slot.name])
        return genome

    def checked(self,genome):
        result=self.evaluate(genome,materialize=True);layout=result['layout'];checked=validate_layout(layout,self.grid,self.config,self.household)
        if checked['pass']!=(result['violations']==0):raise ValueError('Annealing geometry/validator disagreement')
        if checked['pass'] and (abs(checked['fci']-result['fci'])>1e-8 or abs(checked['tb']-result['tb'])>1e-8):raise ValueError('Annealing metric/validator disagreement')
        layout.update({k:checked[k] for k in ['fci','fci_by_variant','tb','served_hours','demanded_hours']});layout['validator']=checked
        return layout


def sum_rectangles(rects,convert):
    result=0
    for rect in rects:result|=convert(rect)
    return result


def anneal(empty,grid,items,candidates,household,config,settings,seed,initial=None,progress=None):
    """Run all prescribed proposals, retaining the best independently valid layout."""
    started=time.perf_counter();initial=initial if initial is not None else footprint(empty,grid,items,candidates,household,config)
    evaluator=Evaluator(grid,items,candidates,household,config,empty,settings)
    base=evaluator.encode(initial);best_genome=base.copy();best=evaluator.checked(base);restarts=[]
    for restart in range(settings['restarts']):
        rng=np.random.default_rng(seed+restart);current=base.copy();value=evaluator.evaluate(current);accepted=0;checked_bests=0
        for iteration in range(settings['iterations']):
            trial=current.copy()
            if len(evaluator.names):
                i=int(rng.integers(len(evaluator.names)));name=evaluator.names[i];states=len(items[name].states);action=rng.random()
                if trial[i,0]<0:
                    trial[i,0]=rng.integers(len(candidates[name]));trial[i,1:]=rng.integers(states)
                elif action<.2:trial[i,0]=-1
                elif action<.6:trial[i,0]=rng.integers(len(candidates[name]))
                else:
                    k=int(rng.integers(1,trial.shape[1]));trial[i,k]=rng.integers(states)
            candidate=evaluator.evaluate(trial)
            temperature=settings['initial_temperature']*(settings['final_temperature']/settings['initial_temperature'])**(iteration/max(1,settings['iterations']-1))
            if candidate['cost']<=value['cost'] or rng.random()<math.exp(min(0.,(value['cost']-candidate['cost'])/temperature)):
                current,value=trial,candidate;accepted+=1
            if candidate['violations']==0 and (candidate['fci']>best['fci']+1e-9 or (abs(candidate['fci']-best['fci'])<=1e-9 and candidate['tb']<best['tb']-1e-9)):
                best=evaluator.checked(trial);best_genome=trial.copy();checked_bests+=1
            if progress is not None and (iteration+1)%1000==0:progress(restart,iteration+1,best['fci'])
        restarts.append(dict(restart=restart,seed=seed+restart,proposals=settings['iterations'],accepted=accepted,new_bests_checked=checked_bests))
    best=evaluator.checked(best_genome);best['algorithm']='simulated_annealing'
    best['annealing']=dict(restarts=restarts,total_proposals=settings['restarts']*settings['iterations'],time_s=time.perf_counter()-started,
        settings=settings,initialization='standalone footprint greedy only',early_stop=False)
    return best
