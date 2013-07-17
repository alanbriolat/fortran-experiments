module ftypes

  implicit none
  public

  integer, parameter :: dp = kind(0.0d0)

  type Foo
    real(dp) :: a
    real :: b
    integer :: c
    logical :: d
    character(len=16) :: e
    real(dp) :: &
       x &
      ,y
  end type Foo

end module ftypes

module ftypes2

  use ftypes

  implicit none
  public

  type :: Bar
    type(Foo) :: f
    real, dimension(20) :: g
  end type Bar

end module ftypes2
