#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_LINE_SIZE 1000
#define MAX_FIELDS 40

void strip_newline(char *str)
{
    size_t len = strlen(str);
    if (len > 0 && str[len - 1] == '\n')
        str[len - 1] = '\0';
    if (len > 0 && str[len - 1] == '\r')
        str[len - 1] = '\0';
}

int main()
{
    FILE *csv_file = fopen("Pecsi_Hawaii_Biolog_PigDecomposition.csv", "r");
    FILE *json_file = fopen("biolog.json", "w");

    if (!csv_file || !json_file)
    {
        printf("Error opening files.\n");
        return 1;
    }

    char line[MAX_LINE_SIZE];
    char *header[MAX_FIELDS];
    int count = 0;

    // read and parse the header Row
    if (fgets(line, sizeof(line), csv_file))
    {
        strip_newline(line);
        char *start = line;
        if ((unsigned char)start[0] == 0xEF && (unsigned char)start[1] == 0xBB && (unsigned char)start[2] == 0xBF) {
            start += 3;
        }
        char *token = strtok(start, ",");
        while (token && count < MAX_FIELDS)
        {
            header[count] = strdup(token);
            count++;
            token = strtok(NULL, ",");
        }
    }

    // start JSON array
    fprintf(json_file, "[\n");

    // read and parse Data Rows
    int is_first_row = 1;
    while (fgets(line, sizeof(line), csv_file))
    {
        strip_newline(line);

        if (!is_first_row)
        {
            fprintf(json_file, ",\n");
        }
        is_first_row = 0;

        fprintf(json_file, "  {\n");

        char *token = strtok(line, ",");
        int i = 0;
        while (token && i < count)
        {
            fprintf(json_file, "    \"%s\": \"%s\"", header[i], token);

            i++;
            token = strtok(NULL, ",");

            if (i < count && token)
            {
                fprintf(json_file, ",\n");
            }
            else
            {
                fprintf(json_file, "\n");
            }
        }
        fprintf(json_file, "  }");
    }

    // end JSON array
    fprintf(json_file, "\n]\n");

    for (int i = 0; i < count; i++)
    {
        free(header[i]);
    }
    fclose(csv_file);
    fclose(json_file);

    return 0;
}
