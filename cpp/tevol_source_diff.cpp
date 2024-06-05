/**
 * @file   tevol_source_diff.hpp
 * @brief  ODE system for research group dynamics in a master equation system
 *
 * Source code. All parameters passed as arguments, but specify and compile to change precision or output format.
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
		 
	//Model parameters	
	double mu = atof(argv[1]); //recruitment 0.25
	double nu_n = atof(argv[2]); // graduation rate of non-programmers 0.01
    double nu_p = atof(argv[3]); // graduation rate of programmers 0.05
    double alpha = atof(argv[4]); // productivity of non-programmer 0.01
    double beta = atof(argv[5]); //productivity of programmers 0.02
    double b = atof(argv[6]); // 0.5
    double c0 = atof(argv[7]); // 0.75
    double K = atof(argv[8]); //group carrying capacity 40
	int    max1 = atoi(argv[9]); //max number of non-programmers 40
    int    max2 = atoi(argv[10]); //max number of programmers 40
    int    IC = atoi(argv[11]); //type of initial conditions
    int    TEMPORAL = atoi(argv[12]); //type of initial conditions
    if(argc<4) {cerr << "Requires a lot of parameters: bla bla bla \n"
                    << endl; return 0;}

    Sparam param = {mu, nu_n, nu_p, alpha, beta, b, c0, K, max1, max2};

    // Integrator parameters
    double t = 0.0;
    double dt = 0.1;
    double t_step = 1.0;
    const double eps_abs = 1e-6;
    const double eps_rel = 1e-8;

    // Setting initial conditions
    typedef boost::multi_array<double,2> mat_type;
    typedef mat_type::index index;
    mat_type y(boost::extents[max1][max2]);
    fill(y.data(),y.data()+y.num_elements(),0.0);

    // Initial conditions 
    double last_avg;
    if(IC==0) {y[0][0] = 1.0; last_avg = 0.0;}
    else if(IC==1) {y[0][max2-1] = 1.0; last_avg = 1.0;}
    else if(IC==3) {y[max1-1][0] = 1.0; last_avg = 0.0;}

    // Define GSL odeiv parameters
    const gsl_odeiv_step_type * step_type = gsl_odeiv_step_rkf45;
    gsl_odeiv_step * step = gsl_odeiv_step_alloc (step_type, max1*max2);
    gsl_odeiv_control * control = gsl_odeiv_control_y_new (eps_abs,eps_rel);
    gsl_odeiv_evolve * evolve = gsl_odeiv_evolve_alloc (max1*max2);
    gsl_odeiv_system sys = {dydt, NULL, static_cast<size_t>(max1*max2), &param};
	

	//Integration
    double last0 = y[0][0];
    double diff = 1.0;
    int status(GSL_SUCCESS);
    for (double t_target = t+t_step; t_target<1000; t_target += t_step ) { //stop by time

        while (t < t_target) {
            status = gsl_odeiv_evolve_apply (evolve,control,step,&sys,&t,t_target,&dt,y.data());
            if (status != GSL_SUCCESS) {
				cout << "SNAFU" << endl;
                break;
			}
        } // end while

        if(TEMPORAL==1) { // When temporal true, record diff at each time step
            diff = abs(last0 - y[0][0]);
            last0 = y[0][0];
            
            if(int(t)%10 == 0)
                double sum = 0.0;
                for(int d1=0; d1<max1; ++d1) {  //loop over number of non-programmers
                    for(int d2=0; d2<max2; ++d2) { //loop over number of programmers
                        cout << t << "," << d1 << "," << d2 << "," << y[d1][d2] << "\n";
                 }
            }
        } else if (TEMPORAL==0) { // just looking at equilibrium; no temporal output.
            double avg = 0.0;
            for(int d1=0; d1<max1; ++d1) {  //loop over number of non-programmers
                for(int d2=0; d2<max2; ++d2) { //loop over number of programmers
                    if(d1+d2>0) avg += (1.0*d2)/(d1+d2)*y[d1][d2];
            }

            diff = abs(last_avg - avg);
            last_avg = avg;
            }
        } // END IFELSE
	} // END FOR

    //final state output 
    if (TEMPORAL==0) {
    
        double avg = 0.0;
        for(int d1=0; d1<max1; ++d1) {  //loop over number of non-programmers
            for(int d2=0; d2<max2; ++d2) { //loop over number of programmers
                if(d1+d2>0) avg += (1.0*d2)/(d1+d2)*y[d1][d2];
            }
        }
        cout << t << "," << mu << ", " << nu_n << ", " << nu_p << ", " << alpha << ", " << beta << ", " << b << ", " << K << ", " << c0 << "," << IC << "," << avg << "\n";

    }

    cout.flush();

    // Free memory
    gsl_odeiv_evolve_free(evolve);
    gsl_odeiv_control_free(control);
    gsl_odeiv_step_free(step);
    
    return 0;
}