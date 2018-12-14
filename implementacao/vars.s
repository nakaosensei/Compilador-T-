	.text
	.file	"vars.ll"
	.globl	main
	.p2align	4, 0x90
	.type	main,@function
main:                                   # @main
	.cfi_startproc
# BB#0:                                 # %entry
	movl	$0, -4(%rsp)
	movl	$1, -8(%rsp)
	movl	$1065353216, -12(%rsp)  # imm = 0x3F800000
	movl	$10, g(%rip)
	movl	$1092616192, h(%rip)    # imm = 0x41200000
	addl	$10, -8(%rsp)
	movss	-12(%rsp), %xmm0        # xmm0 = mem[0],zero,zero,zero
	addss	h(%rip), %xmm0
	movss	%xmm0, -12(%rsp)
	movl	-4(%rsp), %eax
	retq
.Lfunc_end0:
	.size	main, .Lfunc_end0-main
	.cfi_endproc

	.type	g,@object               # @g
	.comm	g,4,4
	.type	h,@object               # @h
	.comm	h,4,4

	.section	".note.GNU-stack","",@progbits
