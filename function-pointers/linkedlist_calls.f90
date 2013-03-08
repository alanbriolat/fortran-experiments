program linkedlist_calls

    use benchmark

    type(ClockType) :: bench
    real :: nums(10000000)
    integer, allocatable :: seed(:)
    integer :: i, seed_n

    interface
        subroutine prototype(x)
            real, intent(inout) :: x
        end subroutine prototype
    end interface

    type ProcPtrList
        procedure(prototype), pointer, nopass :: f
        type(ProcPtrList), pointer :: next
    end type ProcPtrList

    type(ProcPtrList), pointer :: ll, cur

    call random_seed(size=seed_n)
    allocate(seed(seed_n))
    seed = 1234
    call random_seed(put=seed)
    call random_number(nums)

    allocate(ll)
    ll%f => f1
    allocate(ll%next)
    ll%next%f => f2
    allocate(ll%next%next)
    ll%next%next%f => f3
    allocate(ll%next%next%next)
    ll%next%next%next%f => f2
    allocate(ll%next%next%next%next)
    ll%next%next%next%next%f => f1

    call bench%start()
    do i = 1, size(nums)
        cur => ll
        do
            call cur%f(nums(i))
            if (associated(cur%next)) then
                cur => cur%next
            else
                exit
            end if
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

end program linkedlist_calls
