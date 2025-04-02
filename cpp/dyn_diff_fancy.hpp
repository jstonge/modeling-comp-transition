#ifndef DYN_DIFF_HPP_INCLUDED
#define DYN_DIFF_HPP_INCLUDED

#include <boost/multi_array.hpp>
#include <boost/math/distributions/poisson.hpp>
#include <math.h>

using namespace std;

/**
 * @file   dyn_diff.hpp
 * @brief  ODE system for research group dynamics in a master equation system
 *
 * @author  LHD & JSO
 * @since   2025-03-04
 */


struct Sparam {
    const double mu;
    const double nu_n;
    const double nu_p;
    const double ktau;
    const double a;
    const double bl;
    const double kc;
    const double x0c;
    const double K;
    const int max1;
    const int max2;
}; // parameter structure

double cost(double x, double bl, double kc, double x0c, double r) {
    double value = 0.0;    
    value = (1 - r*bl)*(1. / (1. + exp(kc * (x - x0c)))) + bl;
    
    if(value<1.0 && value>0) return value;
    else return 0.0;
}

double B(double x, double bl, double a, double r) {
    double value = 0;
    value = (1. - r*bl)*exp(-a*x) + bl;
    if(value>0) return value;
    else return 0.0;
}

double PI(double x, double a, double bl, double r) {
    double value = 0.0;
    value = (1. - r*bl)*exp(-a*x) + bl;
    if(value>0) return value;
    else return 0.0;
}

double tau(double x, double ktau, double a, double bl, double kc, double x0c, double r) {
    double value = 0.0;
    double tau_rescaling = 20.0;

    value = tau_rescaling*(1.0 / (1.0 + exp(-ktau * (B(x, bl, a, r) - cost(x, bl, kc, x0c, r) + PI(x, a, bl, r)))));

    if(value>0.0) return value;
    else return 0.0;
}

double sigma(int n, int p, double k, double m) {
    double value = m*(n+p+1) * (1.0-(1.0+n+p)/(1.0*k));
    if(value>0) return value;
    else return 0.0;
}


//********** function dydt definition **************************************************************
int dydt(double t, const double y[], double f[], void * param) {
    Sparam& p = *static_cast<Sparam* >(param);

    // Create multi_array reference to y and f
    typedef boost::multi_array_ref<const double,2> CSTmatref_type;
    typedef boost::multi_array_ref<double,2> matref_type;
    
    typedef CSTmatref_type::index indexref;

    // The distribution is in the first (p.max1 * p.max2) entries
    // The final entry is Z.
    CSTmatref_type yref(y, boost::extents[p.max1][p.max2]);
    matref_type    fref(f, boost::extents[p.max1][p.max2]);

    
    // hidden parameters
    double r = 5.0;

    // Process all dynamics
    double R_costDeath = 0.0;
    for(int d1=0; d1<p.max1; ++d1) {  //loop over number of non-programmers
      for(int d2=0; d2<p.max2; ++d2) { //loop over number of programmers

            fref[d1][d2] = 0;
            // const double gsize = d1 + d2;

            if(d1+d2 <= p.K) {

                // birth output ( n,p -> n+1,p)
                if(d1 < p.max1-1.0) { 
                    fref[d1][d2] -= sigma(d1, d2, p.K, p.mu) * yref[d1][d2];
                } // birth input ( n-1,p -> n,p)
                if(d1 > 0.0) {
                    fref[d1][d2] += sigma(d1 - 1.0, d2, p.K, p.mu) * yref[d1 - 1.0][d2];
                }
                
                // non-prog deaths output ( n, p -> n-1, p)
                if(d1 < p.max1 - 1.0) {
                    fref[d1][d2] += p.nu_n * (d1 + 1.0) * yref[d1 + 1.0][d2];
                } // non-prog deaths input ( n, p -> n+1, p)
                fref[d1][d2] -= p.nu_n * d1 * yref[d1][d2];

                // prog deaths output ( n, p -> n, p-1 )
                if(d2 < p.max2 - 1.0) {
                    fref[d1][d2] += p.nu_p * (d2 + 1.0) * yref[d1][d2 + 1.0];
                } // prog deaths input ( n, p -> n, p+1 )
                fref[d1][d2] -= p.nu_p * d2 * yref[d1][d2];

                // non-prog -> prog transitions output
                if ((d1 + d2) > 0.0) {

                    R_costDeath += tau(d2/(d1 + d2), p.ktau, p.a, p.bl, p.kc, p.x0c, r)
                                        * d1
                                        * cost(d2/(d1+d2), p.bl, p.kc, p.x0c, r)
                                        * yref[d1][d2];

                    if (d2 < p.max2-1.0) {
                        // Predation input
                        fref[d1][d2] -= tau(d2/(d1 + d2), p.ktau, p.a, p.bl, p.kc, p.x0c, r)
                            * (1.0 - cost(d2/(d1 + d2), p.bl, p.kc, p.x0c, r))
                            * d1
                            * yref[d1][d2];
                    }
                    
                                            
                    if(d1 < p.max1-1.0 && d2 > 0.0 && d2 < p.max2-1.0) {
                        // Predation output
                        fref[d1][d2] += tau((d2-1.0)/(d1 + d2), p.ktau, p.a, p.bl, p.kc, p.x0c, r)
                                        * (d1 + 1.0)
                                        * (1.0 - cost((d2-1.0)/(d1 + d2), p.bl, p.kc, p.x0c, r))
                                        * yref[d1 + 1][d2 - 1];
                    }
                    
                    
                    fref[d1][d2] -= tau(d2/(d1 + d2), p.ktau, p.a, p.bl, p.kc, p.x0c, r)
                                    * d1
                                    * cost(d2/(d1 + d2), p.bl, p.kc, p.x0c, r)
                                    * yref[d1][d2]; 
                                }

                    // Predation output
                    if(d1 < p.max1 - 1) {
                        fref[d1][d2] += tau(d2/(d1 + d2 + 1.0), p.ktau, p.a, p.bl, p.kc, p.x0c, r)
                                        * (d1 + 1.0)
                                        * cost(d2/(d1 + d2 + 1.0), p.bl, p.kc, p.x0c, r)
                                        * yref[d1 + 1][d2];
                    }
            }
            if (d1==p.max1-1.0 && d2==p.max2-1.0) fref[d1][d2] = R_costDeath;
      }
    }


    return GSL_SUCCESS;

} //********** end function dydt definition ********************************************************

#endif // DYN_DIFF_HPP_INCLUDED
