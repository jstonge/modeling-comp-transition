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
    const double alpha;
    const double beta;
    const double k;
    const double x0;
    const double K;
    const int max1;
    const int max2;
    const int verbose;
}; // parameter structure

// double cost(int n, int p, double c0) {
double cost(int n, int p, double k, double x0) {

    double value = 0.0;
    // if(n>0) value = c0*exp(-3.0*p/(1.0*n));
    // if(n>0) value = c0/(1 + 1.0*(p/n));
    if(n>0) value = 1/(1 + exp(k*( p/n - x0)));
    
    if(value<1 && value>0) return value;
    else return 0.0;
}

double tau(double a, double b, int n, int p, double k, double x0) {

    double value = -a+b*(1-cost(n,p,k,x0));
    return exp(value);
}

double sigma(int n, int p, double k, double m) {
    // limit on group size as sigmoid??
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

    // Compute fraction no-programmer
    double fraction_threshold = 0.05;
    double sumAll    = 0.0;
    double sumNoProg = 0.0;
    for(int d1 = 0; d1 < p.max1; ++d1) {
        for(int d2 = 0; d2 < p.max2; ++d2) {
            double pop = yref[d1][d2];
            sumAll    += pop;
            if(d2 == 0) {
                sumNoProg += pop;
            }
        }
    }
    double fracNoProg = 0.0;
    if (sumAll > 0.0) {
        fracNoProg = sumNoProg / sumAll;
    }

    // Process all dynamics
    for(int d1=0; d1<p.max1; ++d1) {  //loop over number of non-programmers
      for(int d2=0; d2<p.max2; ++d2) { //loop over number of programmers

            fref[d1][d2] = 0;
            
            // births
            if(d1 < p.max1 - 1) {
                fref[d1][d2] -= sigma(d1, d2, p.K, p.mu) * yref[d1][d2];
            }
            if(d1 > 0) {
                fref[d1][d2] += sigma(d1 - 1, d2, p.K, p.mu) * yref[d1 - 1][d2];
            }

            // non-prog deaths
            if(d1 < p.max1 - 1) {
                fref[d1][d2] += p.nu_n * (d1 + 1) * yref[d1 + 1][d2];
            }
            fref[d1][d2] -= p.nu_n * d1 * yref[d1][d2];

            // prog deaths
            if(d2 < p.max2 - 1) {
                fref[d1][d2] += p.nu_p * (d2 + 1) * yref[d1][d2 + 1];
            }
            fref[d1][d2] -= p.nu_p * d2 * yref[d1][d2];

            // non-prog -> prog transitions
            if(d2 > 0 && d1 < p.max1 - 1) {
                fref[d1][d2] += tau(p.alpha, p.beta, d1 + 1, d2 - 1, p.k, p.x0)
                                * (d1 + 1)
                                * (1.0 - cost(d1 + 1, d2 - 1, p.k, p.x0))
                                * yref[d1 + 1][d2 - 1];
            }
            fref[d1][d2] -= tau(p.alpha, p.beta, d1, d2, p.k, p.x0)
                            * d1
                            * (1.0 - cost(d1, d2, p.k, p.x0))
                            * yref[d1][d2];
            
            // cost-based deaths
            if(d1 < p.max1 - 1) {
                fref[d1][d2] += tau(p.alpha, p.beta, d1 + 1, d2, p.k, p.x0)
                                * (d1 + 1)
                                * cost(d1 + 1, d2, p.k, p.x0)
                                * yref[d1 + 1][d2];
            }
            
            fref[d1][d2] -= tau(p.alpha, p.beta, d1, d2, p.k, p.x0)
                            * d1
                            * cost(d1, d2, p.k, p.x0)
                            * yref[d1][d2]; 
      }
    }

    if(p.verbose == 1 && fracNoProg > fraction_threshold) {
        std::cout << "t = " << t
                  << " | Fraction no-programmer (" 
                  << fracNoProg << ") > threshold (" 
                  << fraction_threshold << ")" << std::endl;
    }

    return GSL_SUCCESS;

} //********** end function dydt definition ********************************************************

#endif // DYN_DIFF_HPP_INCLUDED
