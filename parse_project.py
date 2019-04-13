import openpyxl

wb = openpyxl.load_workbook('.\\ref\\in.xlsx')
ws = wb.active

b_col = 2

dev_ranges = list()
for rng in ws.merged_cells:
    if rng.min_col == b_col:
        dev_ranges.append(rng)

dev_ranges = list(reversed(dev_ranges))

for dev in dev_ranges:
    print(ws.cell(*dev.top[0]).value)

wb.close()
