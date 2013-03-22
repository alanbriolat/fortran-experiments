module configstrings
    use iso_c_binding

    type, bind(c) :: ConfigType
        integer(c_int) :: a
        character(kind=c_char,len=8) :: b
        integer(c_int) :: c
    end type ConfigType

    public :: check_config

contains

    subroutine check_config(conf)
        type(ConfigType), intent(in) :: conf
        print *, conf
        print *, len(conf%b), len_trim(conf%b), conf%b == "hello"
    end subroutine check_config

end module configstrings
