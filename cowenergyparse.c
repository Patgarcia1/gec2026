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

int main(){

FILE *csv = fopen("CowEnergyBalanceData-1.csv", "r");
FILE *json = fopen("cowenergy.json", "w");

char line[MAX_LINE_LENGTH];
char *head[max_columns];

int col_count = 0;

if(csv == NULL || json == NULL){
    printf("error opening file\n");
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

    printf("Done! created cowenergy.json\n");

    return 0;
}
