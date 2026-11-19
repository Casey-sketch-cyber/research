
import fs from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';

const [input, target, proof] = process.argv.slice(2);
if (!input || !target) {
  throw new Error('Usage: node build_iscience_table_s4.mjs TableS4-input.json TableS4.xlsx [proof-prefix]');
}
const runtime = process.env.RUNTIME_NODE_MODULES;
const toolkit = runtime
  ? await import(pathToFileURL(createRequire(path.join(runtime, 'artifact-loader.cjs')).resolve('@oai/artifact-tool')).href)
  : await import('@oai/artifact-tool');
const { Workbook, SpreadsheetFile } = toolkit;

const { title, legend, rows } = JSON.parse(await fs.readFile(input, 'utf8'));
if (rows.length !== 49 || rows.some(row => row.length !== 11)) {
  throw new Error('Expected one header and 48 rows of 11 cells');
}

const workbook = Workbook.create();
const dataSheet = workbook.worksheets.add('Table S4');
const legendSheet = workbook.worksheets.add('Legend');
const data = rows.map((row, i) => (
  i === 0 ? row : row.map((value, j) => j > 2 && value !== '—' ? Number(value.replace('−', '-')) : value)
));
dataSheet.getRange('A1:K49').values = data;
dataSheet.showGridLines = false;
dataSheet.freezePanes.freezeRows(1);
const body = dataSheet.getRange('A1:K49');
body.format.font.name = 'Arial';
body.format.font.size = 11;
body.format.font.color = '#162433';
body.format.verticalAlignment = 'center';
body.format.rowHeightPx = 23;
body.format.borders = {
  insideHorizontal: { style: 'thin', color: '#E3E8EE' },
};
const widths = [155, 100, 135, 105, 92, 83, 86, 83, 112, 144, 159];
widths.forEach((width, col) => {
  const letter = String.fromCharCode(65 + col);
  dataSheet.getRange(`${letter}1:${letter}49`).format.columnWidthPx = width;
});
const headers = dataSheet.getRange('A1:K1');
headers.format.fill = '#1E3448';
headers.format.font.bold = true;
headers.format.font.color = '#FFFFFF';
headers.format.wrapText = true;
headers.format.rowHeightPx = 41;
dataSheet.getRange('D2:K49').format.horizontalAlignment = 'right';
dataSheet.getRange('D2:E49').setNumberFormat('0');
for (const letter of ['F', 'G', 'H', 'I', 'K']) {
  dataSheet.getRange(`${letter}2:${letter}49`).setNumberFormat('0.000;"−"0.000');
}
dataSheet.getRange('J2:J49').setNumberFormat('0.0000;"−"0.0000');

legendSheet.showGridLines = false;
legendSheet.getRange('A1:A3').format.columnWidthPx = 805;
legendSheet.getRange('A1:A3').format.font.name = 'Arial';
legendSheet.getRange('A1:A3').format.font.color = '#162433';
legendSheet.getRange('A1').values = [[title]];
legendSheet.getRange('A1').format.rowHeightPx = 62;
legendSheet.getRange('A1').format.font.bold = true;
legendSheet.getRange('A1').format.font.size = 14;
legendSheet.getRange('A1').format.wrapText = true;
legendSheet.getRange('A3').values = [[legend]];
legendSheet.getRange('A3').format.rowHeightPx = 140;
legendSheet.getRange('A3').format.font.size = 11;
legendSheet.getRange('A3').format.verticalAlignment = 'top';
legendSheet.getRange('A3').format.wrapText = true;

const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(target);
if (proof) {
  for (const sheetName of ['Table S4', 'Legend']) {
    const png = await workbook.render({ sheetName, autoCrop: 'all', format: 'png', scale: 1 });
    await fs.writeFile(`${proof}-${sheetName.replace(' ', '')}.png`, new Uint8Array(await png.arrayBuffer()));
  }
}
