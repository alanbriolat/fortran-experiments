program normal_calls

    use benchmark

    type(ClockType) :: bench
    real :: nums(10000000)
    integer, allocatable :: seed(:)
    integer :: i, seed_n

    call random_seed(size=seed_n)
    allocate(seed(seed_n))
    seed = 1234
    call random_seed(put=seed)
    call random_number(nums)

    call bench%start()
    do i = 1, size(nums)
        call f1(nums(i))
        call f2(nums(i))
        call f3(nums(i))
        call f2(nums(i))
        call f1(nums(i))
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

end program normal_calls
