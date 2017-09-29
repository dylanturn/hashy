#define STRING_LENGTH {{STRING_LENGTH}}

typedef struct _Word
{
    uchar text[STRING_LENGTH];
} Word;

__kernel void load_database(__global const Word *word_list, __global long *hash_list, const int word_list_size)
{
    int gid = get_global_id(0);

    if(gid < word_list_size)
    {
        __private ulong value;
        int R = 31; //Small Prime Number
        int M = 65536; //Array Size

        for(int i = 0; i < STRING_LENGTH; i++) {
            value = word_list[gid].text[i];
            //hash_list[gid] = (R * hash_list[gid] + value) % M; //% M
            hash_list[gid] = (R * hash_list[gid] + value) % M;
        }
    }
}