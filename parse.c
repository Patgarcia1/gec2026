#include<stdio.h>
#include<stdlib.h>
#include<string.h>

#define MAX_LINE_LENGTH 1000
#define max_columns 40


//removes new lines and replaces with null terminators
void r_newline(char *str) {
    int len = 0;
    while(str[len] != '\0'){
        len++;
    }
    //Remove all new lines & carriage returns and replace them with null terminators
    while(len > 0 && (str[len - 1] == '\n' || str[len - 1] == '\r')) {
        str[len - 1] = '\0';
        len--;
    }
}

 


int parse_file(const char *csv_name, const char *json_name){

    //first load the csv files
    FILE *csv = fopen(csv_name, "r");
    FILE *json = fopen(json_name, "w");

    
    char line[MAX_LINE_LENGTH];
    char *head[max_columns];

    int col_count = 0;

    //then check if they are loaded correctly.
    if(csv == NULL || json == NULL){

        //handle error
        printf("error opening file\n");
        if(csv) fclose(csv);
        if(json) fclose(json);
        return -1;
    }

    //read the initial header file first
    if(fgets(line, MAX_LINE_LENGTH, csv)){
        r_newline(line);
        char *start = line;

        // Check for UTF-8 BOM and skip it if present
        if ((unsigned char)start[0] == 0xEF && (unsigned char)start[1] == 0xBB && (unsigned char)start[2] == 0xBF) {
            start += 3;
        }
        //get first token (tokens seperated by ",")
        char *token = strtok(start, ",");

        while(token != NULL && col_count < max_columns){

            //read tokens into the head array
            head[col_count] = strdup(token);
            col_count++;
            token = strtok(NULL, ",");
        }
    }

    fprintf(json, "[\n");


    //check if first line
    int is_first_row = 1;

    //read data lines and convert them to JSON format
    while(fgets(line, MAX_LINE_LENGTH, csv)){
        r_newline(line);
        if(!is_first_row){
            //if not first row add comma and newline
            fprintf(json, ",\n");
        }
        is_first_row = 0;

        //start a new json object 
        fprintf(json, "    {\n");
        //start reading tokens from line
        char *token = strtok(line, ",");

        for(int i = 0; i< col_count; i++){
            //first data name 
            fprintf(json, "    \"%s\": ", head[i]);
            if(token){
                //if token exists write it to file
                fprintf(json, "\"%s\"", token);
                token = strtok(NULL, ",");
            }
            else{
                //otherwise write null to file
                fprintf(json, "null");
            }

            //
            if(i < col_count -1){
                fprintf(json, ",");
            }
            fprintf(json, "\n");
        }

        //end the object
        fprintf(json, "    }\n");
    }
    //end json
    fprintf(json, "\n]\n");


    //free memory and close files
    for (int i = 0; i < col_count; i++) {
        free(head[i]);
    }
    fclose(csv);
    fclose(json);

    printf("Done created %s\n", json_name);

    return 0;
}

int main(int argc, char *argv[]){
    if(argc < 2){
        char input_csv[MAX_LINE_LENGTH];
        printf("Enter CSV file name: ");
        if(fgets(input_csv, MAX_LINE_LENGTH, stdin) == NULL){
            return 1;
        }
        r_newline(input_csv);

        if(strlen(input_csv) == 0 || strcmp(input_csv, "all") == 0){
            parse_file("Pecsi_Hawaii_Biolog_PigDecomposition.csv", "biolog.json");
            parse_file("Pecsi_Hawaii_Biogeochem_PigDecomposition.csv", "biogeochem.json");
            parse_file("CowEnergyBalanceData-1.csv", "cowenergy.json");
            return 0;
        }
        else if(strcmp(input_csv, "biolog") == 0 || strcmp(input_csv, "Pecsi_Hawaii_Biolog_PigDecomposition.csv") == 0){
            return parse_file("Pecsi_Hawaii_Biolog_PigDecomposition.csv", "biolog.json");
        }
        else if(strcmp(input_csv, "biochem") == 0 || strcmp(input_csv, "Pecsi_Hawaii_Biogeochem_PigDecomposition.csv") == 0){
            return parse_file("Pecsi_Hawaii_Biogeochem_PigDecomposition.csv", "biogeochem.json");
        }
        else if(strcmp(input_csv, "cow") == 0 || strcmp(input_csv, "CowEnergyBalanceData-1.csv") == 0){
            return parse_file("CowEnergyBalanceData-1.csv", "cowenergy.json");
        }
        else{
            char json_name[MAX_LINE_LENGTH];
            strncpy(json_name, input_csv, MAX_LINE_LENGTH - 1);
            json_name[MAX_LINE_LENGTH - 1] = '\0';
            char *ext = strstr(json_name, ".csv");
            if(ext && strcmp(ext, ".csv") == 0){
                strcpy(ext, ".json");
            } else {
                strncat(json_name, ".json", MAX_LINE_LENGTH - strlen(json_name) - 1);
            }
            return parse_file(input_csv, json_name);
        }
    }

    if(argc == 2){
        if(strcmp(argv[1], "all") == 0){
            parse_file("Pecsi_Hawaii_Biolog_PigDecomposition.csv", "biolog.json");
            parse_file("Pecsi_Hawaii_Biogeochem_PigDecomposition.csv", "biogeochem.json");
            parse_file("CowEnergyBalanceData-1.csv", "cowenergy.json");
            return 0;
        }
        else if(strcmp(argv[1], "biolog") == 0){
            return parse_file("Pecsi_Hawaii_Biolog_PigDecomposition.csv", "biolog.json");
        }
        else if(strcmp(argv[1], "biochem") == 0){
            return parse_file("Pecsi_Hawaii_Biogeochem_PigDecomposition.csv", "biogeochem.json");
        }
        else if(strcmp(argv[1], "cow") == 0){
            return parse_file("CowEnergyBalanceData-1.csv", "cowenergy.json");
        }
        else{
            char json_name[MAX_LINE_LENGTH];
            strncpy(json_name, argv[1], MAX_LINE_LENGTH - 1);
            json_name[MAX_LINE_LENGTH - 1] = '\0';
            char *ext = strstr(json_name, ".csv");
            if(ext && strcmp(ext, ".csv") == 0){
                strcpy(ext, ".json");
            } else {
                strncat(json_name, ".json", MAX_LINE_LENGTH - strlen(json_name) - 1);
            }
            return parse_file(argv[1], json_name);
        }
    }

    if(argc == 3){
        return parse_file(argv[1], argv[2]);
    }

    return 1;
}
