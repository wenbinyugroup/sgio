from pathlib import Path
import sgio

# Wrap in main to prevent execution during test collection
if __name__ == '__main__':
    # Resolve path relative to this test file
    test_dir = Path(__file__).parent
    fn = test_dir / 'files' / 'swiftcomp' / 'sg23_tri6_sc21.sg.k'

    model = sgio.readOutputModel(str(fn), 'sc', smdim=3)
    print(model)
