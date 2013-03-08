program normal_calls

    use benchmark

    type(ClockType) :: bench
    integer :: i

    call bench%start()
    do i = 1, 10000
        print *, "hello world"
    end do
    call bench%stop()

    print *, bench%elapsed

contains

end program normal_calls
