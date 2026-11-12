"""The four frozen surrogate families and validation-only model selection."""
from copy import deepcopy
import json
import time

import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

TARGETS = ("fci_S0", "fci_S2", "saving_m2")
MODELS = ("linear_area", "gbm_features", "mlp_features", "gnn_graph")


def clip_prediction(prediction):
    out = np.maximum(0., prediction)
    out[:, :2] = np.minimum(1., out[:, :2])
    return out


def matrix(features, table, households):
    indicator = {name: np.eye(len(households), dtype=np.float32)[i] for i, name in enumerate(households)}
    return np.stack([np.concatenate([features[row.unit_key].tabular_features, indicator[row.household]])
                     for row in table.itertuples(index=False)])


class TabularSurrogate:
    def __init__(self, name, fits, features, households):
        self.name, self.fits, self.features, self.households = name, fits, features, households

    def prepare(self, table):
        if self.name == "linear_area":
            return len(table), [(hh, table.index.get_indexer(group.index), group[["nia_m2"]].to_numpy())
                                for hh, group in table.groupby("household")]
        return matrix(self.features, table, self.households)

    def predict_batch(self, inputs):
        if self.name == "linear_area":
            size, groups = inputs
            result = np.empty((size, len(TARGETS)), dtype=float)
            for hh, indices, area in groups:
                for j, target in enumerate(TARGETS):
                    result[indices, j] = self.fits[hh, target].predict(area)
        else:
            result = np.column_stack([self.fits[target].predict(inputs) for target in TARGETS])
        return clip_prediction(result)


def fit_tabular(train, val, features, households, seed):
    fits, trials = {}, []
    linear = {}
    for hh in households:
        ht = train[train.household == hh]
        hv = val[val.household == hh]
        for j, target in enumerate(TARGETS):
            observed = ht[ht[target].notna()]
            hold = hv[hv[target].notna()]
            model = LinearRegression().fit(observed[["nia_m2"]].to_numpy(), observed[target])
            linear[hh, target] = model
            prediction = np.clip(model.predict(hold[["nia_m2"]].to_numpy()), 0., 1. if j < 2 else np.inf)
            trials.append(dict(model="linear_area", target=target, household=hh, settings="area-only OLS",
                               validation_mae=float(np.abs(prediction - hold[target]).mean()), selected=True))
    fits["linear_area"] = TabularSurrogate("linear_area", linear, features, households)
    x, v = matrix(features, train, households), matrix(features, val, households)
    grid = {
        "gbm_features": [
            {"max_leaf_nodes": 15, "learning_rate": .07, "max_iter": 150, "l2_regularization": .1},
            {"max_leaf_nodes": 31, "learning_rate": .07, "max_iter": 150, "l2_regularization": 1.},
        ],
        "mlp_features": [
            {"hidden_layer_sizes": (32,), "alpha": .005, "max_iter": 200},
            {"hidden_layer_sizes": (64, 32), "alpha": .02, "max_iter": 200},
        ],
    }
    for name, options in grid.items():
        chosen = {}
        for j, target in enumerate(TARGETS):
            y, yv = train[target].to_numpy(), val[target].to_numpy()
            known, check = np.isfinite(y), np.isfinite(yv)
            candidates = []
            for option in options:
                if name == "gbm_features":
                    model = HistGradientBoostingRegressor(random_state=seed, early_stopping=False, **option)
                else:
                    model = make_pipeline(StandardScaler(), MLPRegressor(random_state=seed, **option))
                model.fit(x[known], y[known])
                pred = np.clip(model.predict(v[check]), 0., 1. if j < 2 else np.inf)
                error = float(np.abs(pred-yv[check]).mean())
                row = dict(model=name, target=target, household="pooled_training", settings=json.dumps(option),
                           validation_mae=error, selected=False, training_count=int(known.sum()),
                           validation_count=int(check.sum()))
                trials.append(row)
                candidates.append((error, model, row))
            best = min(candidates, key=lambda entry: entry[0])
            best[2]["selected"] = True
            chosen[target] = best[1]
        fits[name] = TabularSurrogate(name, chosen, features, households)
    return fits, trials


def standardizer(values):
    mean = values.mean(0)
    scale = values.std(0)
    return mean.astype(np.float32), np.where(scale > 1e-8, scale, 1.).astype(np.float32)


def graph_normalization(features, train, households):
    ids = train.unit_key.unique()
    node_mu, node_sd = standardizer(np.concatenate([features[key].nodes for key in ids]))
    global_mu, global_sd = standardizer(np.stack([features[key].global_features for key in ids]))
    known = train[list(TARGETS)].to_numpy(dtype=np.float32)
    y_mu = np.nanmean(known, axis=0)
    y_sd = np.nanstd(known, axis=0)
    return dict(node_mu=node_mu, node_sd=node_sd, global_mu=global_mu, global_sd=global_sd,
                y_mu=y_mu, y_sd=np.where(y_sd > 1e-8, y_sd, 1.), households=list(households))


def graph_batch(features, table, norm, torch):
    keys = list(dict.fromkeys(table.unit_key))
    mapped = {key: i for i, key in enumerate(keys)}
    nodes, edges, graph_id, globals_ = [], [], [], []
    offset = 0
    for i, key in enumerate(keys):
        plan = features[key]
        nodes.append((plan.nodes-norm["node_mu"])/norm["node_sd"])
        edges.append(plan.edges + offset)
        graph_id.extend([i]*len(plan.nodes))
        globals_.append((plan.global_features-norm["global_mu"])/norm["global_sd"])
        offset += len(plan.nodes)
    row_graph = np.asarray([mapped[key] for key in table.unit_key])
    hh = {h: i for i, h in enumerate(norm["households"])}
    onehot = np.eye(len(hh), dtype=np.float32)[[hh[h] for h in table.household]]
    return (
        torch.from_numpy(np.concatenate(nodes).astype(np.float32)),
        torch.from_numpy(np.concatenate(edges).T.copy()),
        torch.tensor(graph_id, dtype=torch.long),
        torch.from_numpy(np.stack(globals_).astype(np.float32)),
        torch.from_numpy(row_graph),
        torch.from_numpy(onehot),
    )


def create_graphsage(torch, node_dim, global_dim, n_households, hidden):
    nn = torch.nn

    class GraphSAGE(nn.Module):
        def __init__(self):
            super().__init__()
            self.layers = nn.ModuleList([nn.Linear(2*node_dim, hidden), nn.Linear(2*hidden, hidden)])
            self.head = nn.Sequential(nn.Linear(hidden+global_dim+n_households, hidden), nn.ReLU(), nn.Linear(hidden, len(TARGETS)))

        def forward(self, nodes, edges, graph_id, global_features, row_graph, onehot):
            source, destination = edges
            counts = torch.bincount(destination, minlength=len(nodes)).clamp_min(1).view(-1, 1)
            for layer in self.layers:
                neighbor = torch.zeros_like(nodes).index_add_(0, destination, nodes[source])
                nodes = torch.relu(layer(torch.cat([nodes, neighbor/counts], dim=1)))
            pooled = nodes.new_zeros((len(global_features), nodes.shape[1])).index_add_(0, graph_id, nodes)
            sizes = torch.bincount(graph_id, minlength=len(global_features)).view(-1, 1).clamp_min(1)
            pooled = pooled/sizes
            return self.head(torch.cat([pooled[row_graph], global_features[row_graph], onehot], dim=1))

    return GraphSAGE()


class GraphSurrogate:
    def __init__(self, torch, model, norm, features):
        self.torch, self.model, self.norm, self.features = torch, model, norm, features

    def prepare(self, table):
        return graph_batch(self.features, table, self.norm, self.torch)

    def predict_batch(self, inputs):
        self.model.eval()
        with self.torch.no_grad():
            out = self.model(*inputs).numpy()*self.norm["y_sd"] + self.norm["y_mu"]
        return clip_prediction(out)

    def predict(self, table):
        return self.predict_batch(self.prepare(table))


def fit_graph(train, val, features, households, seed, torch, weight_path):
    norm = graph_normalization(features, train, households)
    inputs, validation = graph_batch(features, train, norm, torch), graph_batch(features, val, norm, torch)
    y = train[list(TARGETS)].to_numpy(np.float32)
    observed = torch.from_numpy(np.isfinite(y).astype(np.float32))
    scaled = torch.from_numpy(np.nan_to_num((y-norm["y_mu"])/norm["y_sd"], nan=0.))
    truth = val[list(TARGETS)].to_numpy()
    trials, selected = [], None
    for hidden, learning_rate in [(32, .004), (64, .002)]:
        torch.manual_seed(seed)
        model = create_graphsage(torch, inputs[0].shape[1], inputs[3].shape[1], len(households), hidden)
        surrogate = GraphSurrogate(torch, model, norm, features)
        optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=.01)
        best = None
        for epoch in range(1, 121):
            model.train()
            optimizer.zero_grad()
            loss = (((model(*inputs)-scaled)**2 * observed).sum(0)/observed.sum(0).clamp_min(1)).mean()
            loss.backward()
            optimizer.step()
            if epoch % 4 == 0:
                prediction = surrogate.predict_batch(validation)
                errors = np.nanmean(np.abs(prediction-truth), axis=0)
                score = float(np.mean(errors/norm["y_sd"]))
                if best is None or score < best[0]:
                    best = score, epoch, deepcopy(model.state_dict()), errors
        score, epoch, weights, errors = best
        row = dict(model="gnn_graph", target="joint_normalized_mae", household="pooled_training",
                   settings=json.dumps({"hidden": hidden, "lr": learning_rate, "epochs": 120}),
                   validation_mae=score, best_epoch=epoch, selected=False,
                   val_mae_fci_S0=float(errors[0]), val_mae_fci_S2=float(errors[1]), val_mae_saving_m2=float(errors[2]))
        trials.append(row)
        if selected is None or score < selected[0]:
            selected = score, hidden, weights, row
    _, hidden, weights, row = selected
    row["selected"] = True
    model = create_graphsage(torch, inputs[0].shape[1], inputs[3].shape[1], len(households), hidden)
    model.load_state_dict(weights)
    torch.save(dict(state_dict=weights, hidden=hidden, node_dim=inputs[0].shape[1],
                    global_dim=inputs[3].shape[1], normalization={
                        key: torch.from_numpy(value) if isinstance(value, np.ndarray) else value
                        for key, value in norm.items()
                    }, targets=list(TARGETS)), weight_path)
    reopened = torch.load(weight_path, map_location="cpu", weights_only=True)
    model.load_state_dict(reopened["state_dict"])
    return GraphSurrogate(torch, model, norm, features), trials


def timed_prediction(model, frame, repeats=5):
    """Time a vectorized prediction on the feature-ready test units."""
    inputs = model.prepare(frame)
    predict = lambda: model.predict_batch(inputs)
    result = predict()
    durations = []
    for _ in range(repeats):
        start = time.perf_counter()
        predict()
        durations.append((time.perf_counter()-start)*1000/len(frame))
    return result, float(np.median(durations))
