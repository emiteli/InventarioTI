import pandas as pd


file_path = r'C:\Archlinux\inventario TI\uploads\teste.xlsx'  


df_cleaned = pd.read_excel(file_path, header=1)


df_cleaned = df_cleaned.dropna(how='all', axis=1)  # Remover colunas vazias
df_cleaned = df_cleaned.dropna(how='all')          # Remover linhas vazias


columns_to_keep = ['Unnamed: 0', 'Unnamed: 1', 'Unnamed: 2', 'Unnamed: 3', 'Unnamed: 6', 'Unnamed: 9', 'Unnamed: 8', 'Unnamed: 124']
df_filtered = df_cleaned[columns_to_keep]

df_filtered.columns = ['Filial', 'Cod_Base_Bem', 'Codigo_Item', 'Tipo_Ativo', 'Historico', 'Conta', 'Tipo_Deprec', 'Ativo_Origem']
print(df_filtered.head())
