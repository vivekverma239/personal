import tabula
import pandas as pd
tabula.io.build_options(lattice=True)

def extract_table(file_id, filepath, page, index):
    df2 = tabula.read_pdf(filepath, pages=page)

    if len(df2) <= index + 1:
        return df2[index].to_html()
    else:
        return "[TABLE]"
