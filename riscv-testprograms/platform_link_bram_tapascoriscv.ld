ENTRY(_start)
MEMORY
{
	imem (xai!rw) : ORIGIN = 0x00000000, LENGTH = 64K
	dmem (wa!rxi) : ORIGIN = 0x00010000, LENGTH = 64K
	ctrl (wa!rxi) : ORIGIN = 0x11000000, LENGTH = 1M
}
SECTIONS
{
	__stack_size = 0x1000;
	__indata_size = 0x1000;
	__resdata_size = 0x1000;
	
	. = ORIGIN(imem);
	.text.init : {
			* (.text.init);
	}
	.text : {
	      * (.text);
	}
	
	. = ORIGIN(dmem);
	PROVIDE( _test_indata = ORIGIN(dmem) );
	PROVIDE( _test_resdata = ORIGIN(dmem) + __indata_size );
	.data : {
	    * (.data);	    
	}
	.srodata : {
	      * (.srodata);
	}
	.rodata : {
	      * (.rodata);
	}
	.bss : {
	     * (.bss);
	}
	.note.gnu.build-id : {
	     * (.note.gnu.build-id);
	}
	
	.stack ORIGIN(dmem) + LENGTH(dmem) - __stack_size :
	{
		. = __stack_size;
		PROVIDE( _sp = . );
	}
	
	PROVIDE( _ctrlmem = ORIGIN(ctrl) );
}
