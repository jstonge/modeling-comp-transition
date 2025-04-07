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
 
 #include "dynnn_diff.hpp"
 
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
     int K = stod(argv[4]);
     double ktau = stod(argv[5]);
     double a = stod(argv[6]);
     double kc = stod(argv[7]);
     double x0c = stod(argv[8]);
     double bl = stod(argv[9]);
     double r = stod(argv[10]);
     int max1 = stoi(argv[11]);
     int max2 = stoi(argv[12]);
     int IC = stoi(argv[13]);
     int TEMPORAL = atoi(argv[14]);

     double t_max = (argc > 15) ? stod(argv[15]) : 1000.0;

     Sparam param = {mu, nu_n, nu_p, K, ktau, a, kc, x0c, bl, r, max1, max2};
 
     // Integrator parameters
     double t = 0.0;
     double dt = 0.1;
    //  double t_step = 0.001;
     double t_step = 0.01;
    //  double t_step = 0.5;
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
     } else if (IC == 4) {
        y[max1-1][0] = 1.0; // some ratio
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

     // What we'll track 
     double last0 = 0.0;
     double diff = 1.0;

     double costDeathsCum = 0.0;  // cumulative cost-based deaths
     double t_prev = 0.0;         // track previous time for dt

    // Main loop
    for (double t_target = t + t_step; t < t_max; t_target += t_step) {
    // for (double t_target = t + t_step; diff > 1e-6; t_target += t_step) {
        while (t < t_target) {
            int status = gsl_odeiv_evolve_apply(evolve, control, step, &sys, &t, t_target, &dt, y.data());
            if (status != GSL_SUCCESS) {
                cerr << "GSL integration failed.\n";
                return 1;
            }
        }

        double avg_progs = 0.0;
        for (int d1 = 0; d1 < max1; ++d1) {
            for (int d2 = 0; d2 < max2; ++d2) {
                if(d1+d2>K) continue;
                avg_progs += d2*y[d1][d2];
            }
        }       

        diff = fabs(last0 - avg_progs);
        last0 = avg_progs;

        

            if (TEMPORAL == 1) {
                // Dump full matrix plus the cumulative cost-based deaths
                for (int d1 = 0; d1 < max1; ++d1) {
                    for (int d2 = 0; d2 < max2; ++d2) {
                        if(d1+d2<=K) {
                            cout << t << "," << d1 << "," << d2 << ","
                                << y[d1][d2] << "," 
                                << y[max1-1][max2-1] << "," << avg_progs << "\n";
                        }
                        else cout << t << "," << d1 << "," << d2 << ","
                                << 0.0 << "," 
                                << y[max1-1][max2-1] << "," << avg_progs << "\n";
                    }
                }
                /*cout << t << "," << mu << "," << nu_n << "," << nu_p << ","
                << alpha << "," << beta << "," << k << "," << x0 << ","
                << K << "," << IC << "," << y[max1-1][max2-1] << "," << avg_progs << "\n";*/
            }

        // For equilibrium mode, print final aggregated line
        if (TEMPORAL == 0) {
            double avg = 0.0;
            for (int d1 = 0; d1 < max1; ++d1) {
                for (int d2 = 0; d2 < max2; ++d2) {
                    if (d1 + d2 > 0) {
                        avg += (1.0 * d2)/(d1 + d2) * y[d1][d2];
                    }
                }
            }
            cout << t << "," << mu << "," << nu_n << "," << nu_p << ","
                << K << "," << ktau << "," << a << "," << kc << "," << x0c << ","
                << bl << "," <<  r << "," << IC << "," << avg << "," << y[max1-1][max2-1]  << "\n";
        }
    }

 
     // Cleanup
     gsl_odeiv_evolve_free(evolve);
     gsl_odeiv_control_free(control);
     gsl_odeiv_step_free(step);
 
     return 0;
 }
 