program array_calls

    use benchmark

    type(ClockType) :: bench
    real :: nums(10000000)
    integer, allocatable :: seed(:)
    integer :: i, seed_n, j

    interface
        subroutine prototype(x)
            real, intent(inout) :: x
        end subroutine prototype
    end interface

    type ProcPtr
        procedure(prototype), pointer, nopass :: f
    end type ProcPtr

    type(ProcPtr) :: procs(5)

    call random_seed(size=seed_n)
    allocate(seed(seed_n))
    seed = 1234
    call random_seed(put=seed)
    call random_number(nums)

    procs(1)%f => f1
    procs(2)%f => f2
    procs(3)%f => f3
    procs(4)%f => f2
    procs(5)%f => f1

    call bench%start()
    do i = 1, size(nums)
        do j = 1, size(procs)
            call procs(j)%f(nums(i))
        end do
    end do
    call bench%stop()
    print *, 'Total', bench%elapsed, 'seconds,', bench%elapsed / size(nums), 'per loop' 

contains

    subroutine f1(x)
        real, intent(inout) :: x
        x = acos(x)
    end subroutine f1

    subroutine f2(x)
        real, intent(inout) :: x
        x = cos(x)
    end subroutine f2

    subroutine f3(x)
        real, intent(inout) :: x
        x = -x
    end subroutine f3

end program array_calls
