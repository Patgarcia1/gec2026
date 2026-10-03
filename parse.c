#include<stdio.h>
#include<stdlib.h>
#include<string.h>

#define MAX_LINE_LENGTH 1000
#define max_columns 40

void r_newline(char *str) {
    int len = 0;
    while(str[len] != '\0'){
        len++;
    }
    while(len > 0 && (str[len - 1] == '\n' || str[len - 1] == '\r')) {
        str[len - 1] = '\0';
        len--;
    }
}

int parse_file(const char *csv_name, const char *json_name){
    FILE *csv = fopen(csv_name, "r");
    FILE *json = fopen(json_name, "w");

    char line[MAX_LINE_LENGTH];
    char *head[max_columns];

    int col_count = 0;

    if(csv == NULL || json == NULL){
        printf("error opening file\n");
        if(csv) fclose(csv);
        if(json) fclose(json);
        return 1;
    }

    if(fgets(line, MAX_LINE_LENGTH, csv)){
        r_newline(line);
        char *start = line;
        if ((unsigned char)start[0] == 0xEF && (unsigned char)start[1] == 0xBB && (unsigned char)start[2] == 0xBF) {
            start += 3;
        }
        char *token = strtok(start, ",");

        while(token != NULL && col_count < max_columns){
            head[col_count] = strdup(token);
            col_count++;
            token = strtok(NULL, ",");
        }
    }

    fprintf(json, "[\n");

    int is_first_r = 1;

    while(fgets(line, MAX_LINE_LENGTH, csv)){
        r_newline(line);
        if(!is_first_r){
            fprintf(json, ",\n");
        }
        is_first_r = 0;

        fprintf(json, "    {\n");

        char *token = strtok(line, ",");

        for(int i = 0; i<col_count; i++){
            fprintf(json, "    \"%s\": ", head[i]);

            if(token){
                fprintf(json, "\"%s\"", token);
                token = strtok(NULL, ",");
            }
            else{
                fprintf(json, "null");
            }

            if(i < col_count -1){
                fprintf(json, ",");
            }
            fprintf(json, "\n");
        }
        fprintf(json, "    }\n");
    }
    fprintf(json, "\n]\n");

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
