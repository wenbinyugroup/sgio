"""Custom exceptions for the SGIO library.

This module defines the exception hierarchy for SGIO, including exceptions
for SwiftComp and VABS solver errors, license validation, I/O operations,
and output file processing.

Exception Hierarchy
-------------------
SGIOError
├── SwiftCompError
│   ├── SwiftCompLicenseError
│   └── SwiftCompIOError
├── VABSError
│   ├── VABSLicenseError
│   └── VABSIOError
└── OutputFileError
"""

from __future__ import annotations
from typing import Optional


class SGIOError(Exception):
    """Base exception for all SGIO-related errors.
    
    All custom exceptions in SGIO inherit from this base class,
    allowing users to catch all SGIO-specific exceptions with a
    single except clause.
    """
    pass


class SwiftCompError(SGIOError):
    """Base exception for SwiftComp-related errors.
    
    Raised when the SwiftComp solver encounters an error during execution.
    
    Parameters
    ----------
    message : str, optional
        Error message describing the failure (default: "SwiftComp execution failed")
    return_code : int, optional
        The exit code returned by SwiftComp
    
    Attributes
    ----------
    return_code : int or None
        The exit code returned by SwiftComp
        
    Examples
    --------
    >>> raise SwiftCompError("Failed to initialize", return_code=1)
    SwiftCompError: Failed to initialize (exit code: 1)
    """
    
    def __init__(self, message: str = "SwiftComp execution failed", return_code: Optional[int] = None):
        self.return_code = return_code
        msg = message
        if return_code is not None:
            msg += f" (exit code: {return_code})"
        super().__init__(msg)


class SwiftCompLicenseError(SwiftCompError):
    """Exception raised when SwiftComp license validation fails.
    
    This exception is raised when the SwiftComp solver cannot validate
    its license, the license has expired, or license features are insufficient.
    
    Parameters
    ----------
    message : str, optional
        Error message describing the license failure
    return_code : int, optional
        The exit code returned by SwiftComp
        
    Examples
    --------
    >>> raise SwiftCompLicenseError("License expired")
    SwiftCompLicenseError: License expired
    """
    
    def __init__(self, message: str = "SwiftComp license validation failed", return_code: Optional[int] = None):
        super().__init__(message, return_code)


class SwiftCompIOError(SwiftCompError):
    """Exception raised when SwiftComp I/O operations fail.
    
    This exception is raised when input files cannot be read or written,
    or when SwiftComp output files are missing or corrupted.
    
    Parameters
    ----------
    message : str, optional
        Error message describing the I/O failure
    return_code : int, optional
        The exit code returned by SwiftComp
        
    Examples
    --------
    >>> raise SwiftCompIOError("Cannot read input file")
    SwiftCompIOError: Cannot read input file
    """
    
    def __init__(self, message: str = "SwiftComp I/O operation failed", return_code: Optional[int] = None):
        super().__init__(message, return_code)


class VABSError(SGIOError):
    """Base exception for VABS-related errors.
    
    Raised when the VABS solver encounters an error during execution.
    
    Parameters
    ----------
    message : str, optional
        Error message describing the failure (default: "VABS execution failed")
    return_code : int, optional
        The exit code returned by VABS
    
    Attributes
    ----------
    return_code : int or None
        The exit code returned by VABS
        
    Examples
    --------
    >>> raise VABSError("Failed to compute stiffness", return_code=2)
    VABSError: Failed to compute stiffness (exit code: 2)
    """
    
    def __init__(self, message: str = "VABS execution failed", return_code: Optional[int] = None):
        self.return_code = return_code
        msg = message
        if return_code is not None:
            msg += f" (exit code: {return_code})"
        super().__init__(msg)


class VABSLicenseError(VABSError):
    """Exception raised when VABS license validation fails.
    
    This exception is raised when the VABS solver cannot validate
    its license, the license has expired, or license features are insufficient.
    
    Parameters
    ----------
    message : str, optional
        Error message describing the license failure
    return_code : int, optional
        The exit code returned by VABS
        
    Examples
    --------
    >>> raise VABSLicenseError("License not found")
    VABSLicenseError: License not found
    """
    
    def __init__(self, message: str = "VABS license validation failed", return_code: Optional[int] = None):
        super().__init__(message, return_code)


class VABSIOError(VABSError):
    """Exception raised when VABS I/O operations fail.
    
    This exception is raised when input files cannot be read or written,
    or when VABS output files are missing or corrupted.
    
    Parameters
    ----------
    message : str, optional
        Error message describing the I/O failure
    return_code : int, optional
        The exit code returned by VABS
        
    Examples
    --------
    >>> raise VABSIOError("Output file corrupted")
    VABSIOError: Output file corrupted
    """
    
    def __init__(self, message: str = "VABS I/O operation failed", return_code: Optional[int] = None):
        super().__init__(message, return_code)


class OutputFileError(SGIOError):
    """Exception raised when output file operations fail.
    
    This exception is raised when reading, parsing, or processing
    solver output files fails due to missing files, incorrect format,
    or corrupted data.
    
    Parameters
    ----------
    message : str, optional
        Error message describing the output file failure
    file_path : str, optional
        Path to the problematic output file
        
    Attributes
    ----------
    file_path : str or None
        Path to the problematic output file
        
    Examples
    --------
    >>> raise OutputFileError("Invalid file format", file_path="output.dat")
    OutputFileError: Invalid file format (file: output.dat)
    """
    
    def __init__(self, message: str = "Output file operation failed", file_path: Optional[str] = None):
        self.file_path = file_path
        msg = message
        if file_path is not None:
            msg += f" (file: {file_path})"
        super().__init__(msg)

