#define BUFFER_LENGTH {{BUFFER_LENGTH}}

typedef struct _FileBuffer
{
    uchar value[BUFFER_LENGTH];
} FileBuffer;

__kernel void run_kernel( __global FileBuffer *FileBufferSet, __global long *CRCLookupTable, __global long *CRCHashList, const int file_count)
{
    int gid = get_global_id(0);

    if(gid < file_count)
    {
        __private uint k;

        CRCHashList[gid] ^= 0xffffffff;

        for(int i = 0; i < BUFFER_LENGTH; i++) {
            k = FileBufferSet[gid].value[i];
            CRCHashList[gid] = (CRCHashList[gid] >> 8) ^ CRCLookupTable[(CRCHashList[gid] & 0xff) ^ k];
        }

        CRCHashList[gid] ^= 0xffffffff;
    }
}