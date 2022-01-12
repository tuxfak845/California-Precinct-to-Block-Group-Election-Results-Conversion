#Import necessary libraries
import pandas as pd
import numpy as np

#Adds the values from one column (a new candidate) to an existing table
def addColumn(table, table2):
    new_table = pd.merge(
            left=table,
            right=table2,
            on="BlockGroup",
            how='left'
        )
    return new_table

#Main function: Assigns votes for a particular candidate (column) to block groups
def assign_column (column, sov, blk_conv):
    #Make sure SRPREC_KEY is a string so we can use it to join 
    blk_conv['SRPREC_KEY'] = blk_conv['SRPREC_KEY'].astype(str)
    #Make sure each SRPREC_KEY has a 0 in front of it
    key_sans_zero = blk_conv[blk_conv["SRPREC_KEY"].str[0:1] != "0"]
    blk_conv.loc[blk_conv["SRPREC_KEY"].str[0:1] != "0", "SRPREC_KEY"] = "0" + blk_conv["SRPREC_KEY"]
    #Join the block-precinct conversions to the precinct results, this is the equivalent of an xlookup or vlookup
    merged_res = pd.merge(
        left=blk_conv,
        right=sov,
        on="SRPREC_KEY",
        how='left'
    )
    #Make sure that the individual block keys are strings
    merged_res['BLOCK_KEY'] = merged_res['BLOCK_KEY'].astype(str)
    #Derive the block group key from the block key (first 12 digits of block id)
    merged_res["BlockGroup"] = "0" + merged_res["BLOCK_KEY"].str.slice(stop = 11)
    #Assign precinct votes to blocks - PCTSRPREC is % of registered voters in an SRPREC that are from a particular block
    col_blk_name = column + "_BLK"
    merged_res[col_blk_name] = merged_res[column] * merged_res["PCTSRPREC"] / 100
    #Pivot table: sum the values of the candidate totals for each block group
    table = pd.pivot_table(merged_res, 
            values=[col_blk_name], index=["BlockGroup"], aggfunc=np.sum)
    return table

#User Interface
print("Welcome! This application helps convert California election results from precincts to block groups.")
print("")
print("Before starting, please make sure that you have downloaded the CSV files for both the statement of vote by SRPREC and the SRPREC to 2010 BLK conversion from Statewide Database.")
print("Please make sure that they are in the same directory as this python file.")
print("")
print("What is the name of the CSV file containing the statement of votes by SRPREC?")
sov = pd.read_csv(input())
print("What is the name of the CSV file containing the SRPREC to 2010 BLK conversions?")
blk_conv = pd.read_csv(input())
print("I will now ask you which columns from the SOV you would like to assign to block groups.\nPlease enter the column names EXACTLY as they are found in the SOV files from Statewide Database.\nFor example, Joe Biden's votes in 2020 would be PRSDEM01.")
print("What is the first column you would like to assign?")
col1 = input()
results_table = assign_column(col1, sov, blk_conv)

not_done = True
while not_done:
    print("Do you have any other columns? Y or N")
    if input() == "Y":
        print("What is the next column you would like to assign?")
        colname = input()
        new_table = assign_column(colname, sov, blk_conv)
        results_table = addColumn (results_table, new_table)
    elif input() == "N":
        print("What would you like the CSV with the converted results to be named?")
        csv_name = input()
        results_table.to_csv(csv_name)
        print("Thank you for using this service. The file with your results should be in the directory same directory as this python file.")
        not_done = False
    else:
        print("Please input either Y or N.")





