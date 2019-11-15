__doc__ = """ Boundary conditions for rod test module """
import sys

# System imports
import numpy as np
from test_rod import TestRod
from elastica.boundary_conditions import FreeRod, OneEndFixedRod, HelicalBucklingBC
from numpy.testing import assert_allclose
from elastica.utils import Tolerance
from pytest import main


# tests free rod boundary conditions
def test_free_rod():
    test_rod = TestRod()
    free_rod = FreeRod()
    test_position = np.random.rand(3, 20)
    test_rod.position = (
        test_position.copy()
    )  # We need copy of the list not a reference to this array
    test_directors = np.random.rand(3, 3, 20)
    test_rod.directors = (
        test_directors.copy()
    )  # We need copy of the list not a reference to this array
    free_rod.constrain_values(test_rod, time=0)
    assert_allclose(test_position, test_rod.position, atol=Tolerance.atol())
    assert_allclose(test_directors, test_rod.directors, atol=Tolerance.atol())

    test_velocity = np.random.rand(3, 20)
    test_rod.velocity = (
        test_velocity.copy()
    )  # We need copy of the list not a reference to this array
    test_omega = np.random.rand(3, 20)
    test_rod.omega = (
        test_omega.copy()
    )  # We need copy of the list not a reference to this array
    free_rod.constrain_rates(test_rod, time=0)
    assert_allclose(test_velocity, test_rod.velocity, atol=Tolerance.atol())
    assert_allclose(test_omega, test_rod.omega, atol=Tolerance.atol())


def test_one_end_fixed_rod():

    test_rod = TestRod()
    start_position = np.random.rand(3)
    start_directors = np.random.rand(3, 3)
    fixed_rod = OneEndFixedRod(start_position, start_directors)
    test_position = np.random.rand(3, 20)
    test_rod.position = (
        test_position.copy()
    )  # We need copy of the list not a reference to this array
    test_directors = np.random.rand(3, 3, 20)
    test_rod.directors = (
        test_directors.copy()
    )  # We need copy of the list not a reference to this array
    fixed_rod.constrain_values(test_rod, time=0)
    test_position[..., 0] = start_position
    test_directors[..., 0] = start_directors
    assert_allclose(test_position, test_rod.position, atol=Tolerance.atol())
    assert_allclose(test_directors, test_rod.directors, atol=Tolerance.atol())

    test_velocity = np.random.rand(3, 20)
    test_rod.velocity = (
        test_velocity.copy()
    )  # We need copy of the list not a reference to this array
    test_omega = np.random.rand(3, 20)
    test_rod.omega = (
        test_omega.copy()
    )  # We need copy of the list not a reference to this array
    fixed_rod.constrain_rates(test_rod, time=0)
    test_velocity[..., 0] = np.array((0, 0, 0))
    test_omega[..., 0] = np.array((0, 0, 0))
    assert_allclose(test_velocity, test_rod.velocity, atol=Tolerance.atol())
    assert_allclose(test_omega, test_rod.omega, atol=Tolerance.atol())


def test_helical_buckling_bc():

    twisting_time = 500.0
    slack = 3.0
    number_of_rotations = 27.0  # number of 2pi rotations
    start_position = np.array([0.0, 0.0, 0.0])
    start_directors = np.identity(3, float)
    end_position = np.array([100.0, 0.0, 0.0])
    end_directors = np.identity(3, float)

    test_rod = TestRod()

    test_position = np.random.rand(3, 20)
    test_position[..., 0] = start_position
    test_position[..., -1] = end_position
    test_rod.position = (
        test_position.copy()
    )  # We need copy of the list not a reference to this array
    test_directors = np.tile(np.identity(3, float), 20).reshape(3, 3, 20)
    test_directors[..., 0] = start_directors
    test_directors[..., -1] = end_directors
    test_rod.directors = (
        test_directors.copy()
    )  # We need copy of the list not a reference to this array

    test_velocity = np.random.rand(3, 20)
    test_rod.velocity = (
        test_velocity.copy()
    )  # We need copy of the list not a reference to this array
    test_omega = np.random.rand(3, 20)
    test_rod.omega = (
        test_omega.copy()
    )  # We need copy of the list not a reference to this array
    position_start = test_rod.position[..., 0]
    position_end = test_rod.position[..., -1]
    director_start = test_rod.directors[..., 0]
    director_end = test_rod.directors[..., -1]
    helicalbuckling_rod = HelicalBucklingBC(
        position_start,
        position_end,
        director_start,
        director_end,
        twisting_time,
        slack,
        number_of_rotations,
    )

    # Check Neumann BC
    # time < twisting time
    time = twisting_time - 1.0

    helicalbuckling_rod.constrain_rates(test_rod, time=time)
    test_velocity[..., 0] = np.array([0.003, 0.0, 0.0])
    test_velocity[..., -1] = -np.array([0.003, 0.0, 0.0])
    test_omega[..., 0] = np.array([0.169646, 0.0, 0.0])
    test_omega[..., -1] = -np.array([0.169646, 0.0, 0.0])

    assert_allclose(test_velocity, test_rod.velocity, atol=Tolerance.atol())
    assert_allclose(test_omega, test_rod.omega, atol=Tolerance.atol())

    # time > twisting time
    time = twisting_time + 1
    helicalbuckling_rod.constrain_rates(test_rod, time=time)
    test_velocity[..., 0] = np.array((0, 0, 0))
    test_velocity[..., -1] = np.array((0, 0, 0))
    test_omega[..., 0] = np.array((0, 0, 0))
    test_omega[..., -1] = np.array((0, 0, 0))
    assert_allclose(test_velocity, test_rod.velocity, atol=Tolerance.atol())
    assert_allclose(test_omega, test_rod.omega, atol=Tolerance.atol())

    # Check Dirichlet BC

    helicalbuckling_rod.constrain_values(test_rod, time=time)

    test_position[..., 0] = np.array([1.5, 0.0, 0.0])
    test_position[..., -1] = np.array([98.5, 0.0, 0.0])

    test_directors[..., 0] = np.array(
        [[1.0, 0.0, 0.0], [0.0, -1.0, -6.85926004e-15], [0.0, 6.85926004e-15, -1.0]]
    )

    test_directors[..., -1] = np.array(
        [[1.0, 0.0, 0.0], [0.0, -1.0, 6.85926004e-15], [0.0, -6.85926004e-15, -1.0]]
    )

    assert_allclose(test_position, test_rod.position, atol=Tolerance.atol())
    assert_allclose(test_directors, test_rod.directors, atol=Tolerance.atol())


if __name__ == "__main__":
    main([__file__])