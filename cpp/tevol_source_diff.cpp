/**
 * @file   tevol_source_diff.hpp
 * @brief  ODE system for research group dynamics in a master equation system
 *
 * Compile with:
 * g++ -std=c++11 -O3 -o tevol_source_diff ./tevol_source_diff.cpp $(gsl-config --cflags) $(gsl-config --libs)
 *
 * @author  LHD + JSO
 * @since   2023-11-28
 */

 #include <iostream>
 #include <cmath>
 #include <algorithm>
 #include <vector>
 #include <fstream>
 #include <sstream>
 
 #include <boost/multi_array.hpp>
 #include <gsl/gsl_errno.h>
 #include <gsl/gsl_odeiv.h>
 
 #include "dyn_diff.hpp"
 
 using namespace std;
 
 int main(int argc, const char *argv[]) {
     
     if(argc < 13) {
         cerr << "Usage: ./tevol_source_diff mu nu_n nu_p alpha beta k x0 K max1 max2 IC TEMPORAL [t_max]\n";
         return 1;
     }
 
     // Model parameters
     double mu = stod(argv[1]);
     double nu_n = stod(argv[2]);
     double nu_p = stod(argv[3]);
     double alpha = stod(argv[4]);
     double beta = stod(argv[5]);
     double k = stod(argv[6]);
     double x0 = stod(argv[7]);
     double K = stod(argv[8]);
     int max1 = stoi(argv[9]);
     int max2 = stoi(argv[10]);
     int IC = stoi(argv[11]);
     int TEMPORAL = stoi(argv[12]);
 
     double t_max = (argc > 13) ? stod(argv[13]) : 1000.0;
 
     Sparam param = {mu, nu_n, nu_p, alpha, beta, k, x0, K, max1, max2};
 
     // Integrator parameters
     double t = 0.0;
     double dt = 0.1;
     double t_step = 1.0;
     const double eps_abs = 1e-6;
     const double eps_rel = 1e-8;
 
     // State space (probability matrix)
     typedef boost::multi_array<double, 2> mat_type;
     mat_type y(boost::extents[max1][max2]);
     fill(y.data(), y.data() + y.num_elements(), 0.0);
 
     // Initial condition
     double last_avg = 0.0;
     if (IC == 0) {
         y[0][0] = 1.0; // all non-programmers
         last_avg = 0.0;
     } else if (IC == 1) {
         y[0][max2 - 1] = 1.0; // all programmers
         last_avg = 1.0;
     } else if (IC == 3) {
         y[max1 - 1][0] = 1.0; // large group, all non-programmers
         last_avg = 0.0;
     } else {
         cerr << "Invalid IC value.\n";
         return 1;
     }
 
     // GSL setup
     const gsl_odeiv_step_type *step_type = gsl_odeiv_step_rkf45;
     gsl_odeiv_step *step = gsl_odeiv_step_alloc(step_type, max1 * max2);
     gsl_odeiv_control *control = gsl_odeiv_control_y_new(eps_abs, eps_rel);
     gsl_odeiv_evolve *evolve = gsl_odeiv_evolve_alloc(max1 * max2);
     gsl_odeiv_system sys = {dydt, NULL, static_cast<size_t>(max1 * max2), &param};
 
     // Integration loop
     double last0 = y[0][0];
     double diff = 1.0;
 
     for (double t_target = t + t_step; t_target < t_max; t_target += t_step) {
         while (t < t_target) {
             int status = gsl_odeiv_evolve_apply(evolve, control, step, &sys, &t, t_target, &dt, y.data());
             if (status != GSL_SUCCESS) {
                 cerr << "GSL integration failed.\n";
                 return 1;
             }
         }
 
         if (TEMPORAL == 1) {
             // Temporal output mode: dump full matrix every 10 steps
             diff = abs(last0 - y[0][0]);
             last0 = y[0][0];
 
             if (static_cast<int>(t) % 10 == 0) {
                 for (int d1 = 0; d1 < max1; ++d1) {
                     for (int d2 = 0; d2 < max2; ++d2) {
                        //  cout << t << "," << d1 << "," << d2 << "," << y[d1][d2] << "\n";
                     }
                 }
             }
 
         } else if (TEMPORAL == 0) {
             // Equilibrium mode: track average fraction of programmers
             double avg = 0.0;
             for (int d1 = 0; d1 < max1; ++d1) {
                 for (int d2 = 0; d2 < max2; ++d2) {
                     if (d1 + d2 > 0)
                         avg += (1.0 * d2) / (d1 + d2) * y[d1][d2];
                 }
             }
             diff = abs(last_avg - avg);
             last_avg = avg;
         }
     }
 
     // Final output (for equilibrium mode)
     if (TEMPORAL == 0) {
         double avg = 0.0;
         for (int d1 = 0; d1 < max1; ++d1) {
             for (int d2 = 0; d2 < max2; ++d2) {
                 if (d1 + d2 > 0)
                     avg += (1.0 * d2) / (d1 + d2) * y[d1][d2];
             }
         }
         cout << t << "," << mu << "," << nu_n << "," << nu_p << ","
              << alpha << "," << beta << "," << k << "," << x0 << ","
              << K << "," << IC << "," << avg << "\n";
     }
 
     // Cleanup
     gsl_odeiv_evolve_free(evolve);
     gsl_odeiv_control_free(control);
     gsl_odeiv_step_free(step);
 
     return 0;
 }
 