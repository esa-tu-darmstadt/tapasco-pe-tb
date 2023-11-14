#define CTRLMEM_BASE 0x11000000
#define CTRLMEM_RESULTLO = (volatile unsigned int*)(CTRLMEM_BASE+0x10)
#define CTRLMEM_RESULTHI = (volatile unsigned int*)(CTRLMEM_BASE+0x14)
#define CTRLMEM_ARG(i) (volatile unsigned int*)(CTRLMEM_BASE+0x20+((i)*0x10))

void testfn()
{
	//Do nothing
}

int main()
{
	for (int i = 0; i < 2; ++i)
		testfn();
	return 0;
}
