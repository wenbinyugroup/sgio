Merge "sg21eb_tri3_vabs40.msh";
//+
Point(1) = {0, 0, 0, 1.0};
//+
Point(2) = {0, 0, 0, 1.0};
//+
SetFactory("OpenCASCADE");
Circle(1) = {0, 0, 0, 1.1, 0, 2*Pi};
//+
Sphere(1) = {0, 0, 0, 0.05, -Pi/2, Pi/2, 2*Pi};
