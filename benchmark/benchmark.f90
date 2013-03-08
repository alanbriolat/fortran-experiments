module benchmark

    integer, parameter, private :: dp = kind(0.d0)

    type ClockType
        integer(8) :: count_rate
        integer(8) :: count_start
        integer(8) :: count_end
        real(dp) :: elapsed
    contains
        procedure, pass :: start
        procedure, pass :: stop
    end type ClockType

contains

    subroutine start(c)
        class(ClockType), intent(inout) :: c
        call system_clock(c%count_start, c%count_rate)
    end subroutine start

    subroutine stop(c)
        class(ClockType), intent(inout) :: c
        call system_clock(c%count_end)
        c%elapsed = (c%count_end - c%count_start) / real(c%count_rate, kind=dp)
    end subroutine stop

end module benchmark
