"""
Example 1: Basic SGIO Logging Setup

This example demonstrates the simplest way to configure SGIO logging
for a single-package application.
"""

import sgio

# Configure SGIO logging with default settings
# - Console output at INFO level
# - File output at INFO level  
# - Logs append to 'run.log'
# - Propagation enabled (for future multi-package integration)
sgio.configure_logging(
    cout_level='INFO',
    fout_level='DEBUG',
    filename='run.log'
)

# Now use SGIO - all logs will appear in console and run.log
print("\n=== Example 1: Basic SGIO Logging ===\n")

# The logger is already available
sgio.logger.info("SGIO logging is configured")
sgio.logger.debug("This debug message appears in file but not console")
sgio.logger.warning("This is a warning message")

# Use SGIO functions - they will log automatically
# For this example, we'll just demonstrate logger usage
print("\nSimulating SGIO operations...")

for i in range(3):
    sgio.logger.info(f"Processing step {i+1}/3")
    sgio.logger.debug(f"Detailed information for step {i+1}")

sgio.logger.info("Processing complete!")

print("\n✓ Logs written to 'run.log'")
print("✓ Console shows INFO and above")
print("✓ File contains DEBUG and above")
