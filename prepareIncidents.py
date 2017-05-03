#script to prepare the data for hierarchical regression
import pandas
import sys

def change_names(df,column):
	df[column] = df[column].str.replace(' \(the\)','')
	df[column] = df[column].str.replace('Dem. ','Democratic ')
	df[column] = df[column].str.replace('Fed. ','Federated ')
	df[column] = df[column].str.replace('The former Yugoslav Republic of','TFYR')
	df[column] = df[column].str.replace('of Great Britain and Northern Ireland','')

if __name__ == "__main__":
	incidenceFile = sys.argv[1]
	df = pandas.read_csv(incidenceFile)
	change_names(df,'Cname')
	incidence = pandas.melt(df,id_vars=list(df.columns[0:4]),value_vars=list(df.columns[4:]))
	incidence.rename(columns={'variable':'year','value':'incidents'},inplace=True)
	incidence = incidence.dropna()
	populationFile = 'population.csv'
	df = pandas.read_csv(populationFile)
	change_names(df,'country')
	population = pandas.melt(df,id_vars=list(df.columns[0:3]),value_vars=list(df.columns[3:]))
	population.rename(columns={'variable':'year','value':'population'},inplace=True)
	coverageFile = sys.argv[2]
	df = pandas.read_csv(coverageFile)
	change_names(df,'Cname')
	coverage = pandas.melt(df,id_vars=list(df.columns[0:4]),value_vars=list(df.columns[4:]))
	coverage.rename(columns={'variable':'year','value':'coverage'},inplace=True)
	coverage = coverage.dropna()
	coverage.coverage = coverage.coverage/100.0
	
	#we want a new table with the year, region, country, incidence percent, coverage percent
	incidence2 = incidence.merge(population,how='inner',left_on=['Cname','year'],right_on=['country','year'])[['WHO_REGION','region','country','year','incidents','population']]
	incidence2['percent_incidence'] = incidence2.incidents / incidence2.population / 1000.
	data = coverage.merge(incidence2,how='inner',left_on=['Cname','year'],right_on=['country','year'])[['WHO_REGION','region','country','year','percent_incidence','coverage']]
	data.to_csv(sys.argv[3],header=True,index=False)
	
	data.year = data.year.astype(int)
	data['prevYear'] = data.year - 1
	data2 = data.merge(data,how='inner',left_on=['country','prevYear'],right_on=['country','year'])[['WHO_REGION_x','region_x','country','year_x','percent_incidence_x','coverage_x','percent_incidence_y']]
	data2.columns = ['WHO_REGION','region','country','year','percent_incidence','coverage','prev_percent_incidence']
	data2.to_csv(sys.argv[3],header=True,index=False)