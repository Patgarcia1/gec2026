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

FILE *csv = fopen("Pecsi_Hawaii_Biogeochem_PigDecomposition.csv", "r");

char line[MAX_LINE_LENGTH];
char *head[max_columns];

int col_count = 0;

if(csv == NULL){
    perror("error opening file");
    return EXIT_FAILURE;
}

if(fgets(line, MAX_LINE_LENGTH, csv)){
    r_newline(line);
    char *token = strtok(line, ",");

    while(token != NULL && col_count < max_columns){
        head[col_count] = strdup(token);
        col_count++;
        token = strtok(NULL, ",");
    }
}

printf("[\n");

int is_first_r = 1;

while(fgets(line, MAX_LINE_LENGTH, csv)){
    r_newline(line);
    if(!is_first_r){
        printf(",\n");
    }
    is_first_r = 0;

    printf("    {\n");

    char *token = strtok(line, ",");

    for(int i = 0; i<col_count; i++){
        printf("    \"%s\": ", head[i]);

        if(token){
            printf("\"%s\"", token);
                token = strtok(NULL, ",");
        }
        else{
            printf("null");
        }

       if(i < col_count -1){
        printf(",");
       }
       printf("\n");
    }
    printf("    }\n");
}
printf("\n]\n");
 

    for (int i = 0; i < col_count; i++) {
        free(head[i]);
    }
    fclose(csv);

    return 0;
}