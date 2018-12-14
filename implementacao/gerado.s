	.text
	.file	"gerado.ll"
	.globl	LeiaInteiro
	.p2align	4, 0x90
	.type	LeiaInteiro,@function
LeiaInteiro:                            # @LeiaInteiro
	.cfi_startproc
# BB#0:                                 # %LeiaEntry
	movl	$5, %eax
	retq
.Lfunc_end0:
	.size	LeiaInteiro, .Lfunc_end0-LeiaInteiro
	.cfi_endproc

	.globl	EscrevaInteiro
	.p2align	4, 0x90
	.type	EscrevaInteiro,@function
EscrevaInteiro:                         # @EscrevaInteiro
	.cfi_startproc
# BB#0:                                 # %EscrevaEntry
	movl	$1, %eax
	retq
.Lfunc_end1:
	.size	EscrevaInteiro, .Lfunc_end1-EscrevaInteiro
	.cfi_endproc

	.globl	main
	.p2align	4, 0x90
	.type	main,@function
main:                                   # @main
	.cfi_startproc
# BB#0:                                 # %mainEntry
	pushq	%rbp
.Ltmp0:
	.cfi_def_cfa_offset 16
.Ltmp1:
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
.Ltmp2:
	.cfi_def_cfa_register %rbp
	movq	%rsp, %rax
	leaq	-16(%rax), %rsp
	movl	$0, -16(%rax)
	xorl	%eax, %eax
	movq	%rbp, %rsp
	popq	%rbp
	retq
.Lfunc_end2:
	.size	main, .Lfunc_end2-main
	.cfi_endproc


	.section	".note.GNU-stack","",@progbits
