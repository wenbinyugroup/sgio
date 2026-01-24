"""Performance tests for Tsai-Wu failure criterion vectorization."""

import numpy as np
import time
from sgio.model.failure import TsaiWuFailureCriterion


def test_vectorization_performance():
    """Demonstrate performance benefits of vectorization."""
    
    # Create a typical composite material
    criterion = TsaiWuFailureCriterion(
        xt=1500.0, xc=1200.0,
        yt=50.0, yc=150.0,
        zt=50.0, zc=150.0,
        r=70.0, t=70.0, s=70.0
    )
    
    # Generate test data
    n = 10000
    stresses = np.random.rand(n, 6) * 100
    
    # Test vectorized approach
    start = time.time()
    fi_vectorized = criterion.failure_index(stresses)
    sr_vectorized = criterion.strength_ratio(stresses)
    vectorized_time = time.time() - start
    
    # Test loop approach (for comparison)
    start = time.time()
    fi_loop = np.array([criterion.failure_index(stress) for stress in stresses])
    sr_loop = np.array([criterion.strength_ratio(stress) for stress in stresses])
    loop_time = time.time() - start
    
    # Verify results are the same
    np.testing.assert_allclose(fi_vectorized, fi_loop, rtol=1e-10)
    np.testing.assert_allclose(sr_vectorized, sr_loop, rtol=1e-10)
    
    # Print performance comparison
    speedup = loop_time / vectorized_time
    print(f"\nPerformance comparison for {n} stress vectors:")
    print(f"  Vectorized approach: {vectorized_time:.4f} seconds")
    print(f"  Loop approach:       {loop_time:.4f} seconds")
    print(f"  Speedup:             {speedup:.2f}x")
    
    # Vectorized should be faster
    assert vectorized_time < loop_time, "Vectorized approach should be faster"
    print(f"\n✓ Vectorization is {speedup:.2f}x faster!")


if __name__ == "__main__":
    test_vectorization_performance()

