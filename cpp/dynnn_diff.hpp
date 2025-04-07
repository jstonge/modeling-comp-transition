#ifndef DYN_DIFF_HPP_INCLUDED
#define DYN_DIFF_HPP_INCLUDED

#include <boost/multi_array.hpp>
#include <boost/math/distributions/poisson.hpp>
#include <math.h>

using namespace std;

/**
 * @file   dynnn_diff.hpp
 * @brief  ODE system for research group dynamics in a master equation system
 *
 * @author  LHD & JSO
 * @since   2025-03-04
 */


struct Sparam {
    const double mu;
    const double nu_n;
    const double nu_p;
    const int K;
    const double ktau;
    const double a;
    const double kc;
    const double x0c;
    const double bl;
    const double r;
    const int max1;
    const int max2;
}; // parameter structure



double B(double x, double a, double bl, double r) {
    return (1.0 - r*bl)*exp(-a*x) + bl;
}

double PI(double x, double a, double bl, double r) {
    return (1.0 - r*bl)*exp(-a*x) + bl;
}

double C(double x, double kc, double x0c, double bl, double r) {
    return (1.0 - r*bl) * (1.0 / (1.0 + exp(kc * (x - x0c)))) + bl;
}

double tau(double x, double ktau, double a, double kc, double x0c, double bl, double r) {
double TAU_RESCALING = 5.0;
    double netpayoff = B(x,a,bl,r) - C(x,kc,x0c,bl,r) + PI(x,a,bl,r);
    return TAU_RESCALING * (1.0 / (1.0 + exp(-ktau * netpayoff)));
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
    double R_costDeath = 0.0;
    for(int d1=0; d1<p.max1; ++d1) {  //loop over number of non-programmers
      for(int d2=0; d2<p.max2; ++d2) { //loop over number of programmers
            
        fref[d1][d2] = 0;
        
        // there's always a PI in the group
        int gsize = d1 + d2 + 1;

        if((d1+d2)<=p.K) {
                
            R_costDeath += tau((d2*1.0)/(gsize*1.0), p.ktau, p.a, p.kc, p.x0c, p.bl, p.r)
                * d1
                * C((d2*1.0)/(gsize*1.0), p.kc, p.x0c, p.bl, p.r)
                * yref[d1][d2];
                
            // -----------------------------------------------------------
            // Outflows
            fref[d1][d2] -= p.nu_p * d2 * yref[d1][d2];
            fref[d1][d2] -= p.nu_n * d1 * yref[d1][d2];
            if(d1 < p.max1 - 1 && gsize < p.K) { 
                fref[d1][d2] -= p.mu * gsize * (1.0 - (gsize*1.0)/(1.0*p.K)) * yref[d1][d2]; 
            } 

            // -----------------------------------------------------------
            // Inflows
            if(d2 < p.max2 - 1) { fref[d1][d2] += p.nu_p * (d2 + 1) * yref[d1][d2 + 1]; }
            if(d1 < p.max1 - 1) { fref[d1][d2] += p.nu_n * (d1 + 1) * yref[d1+1][d2]; }
            if(d1 > 0 && (gsize-1) < p.K) { 
                fref[d1][d2] += p.mu * (gsize-1) * (1.0 - (gsize-1.0)/(1.0*p.K)) * yref[d1-1][d2]; 
            }
            
            // -----------------------------------------------------------
            // Predation
            if(d2 < p.max2 - 1 && d1 > 0) {
                fref[d1][d2] -= tau((d2*1.0)/(gsize*1.0), p.ktau, p.a, p.kc, p.x0c, p.bl, p.r)
                                * (1. - C((d2*1.0)/(gsize*1.0), p.kc, p.x0c, p.bl, p.r))
                                * d1
                                * yref[d1][d2];
            }

            if(d2 > 0 && d1 < p.max1 - 1 && d2 < p.max2 ) {
                fref[d1][d2] += tau((d2-1.0)/(gsize*1.0), p.ktau, p.a, p.kc, p.x0c, p.bl, p.r)
                                * (1.0 - C((d2-1.0)/(gsize*1.0), p.kc, p.x0c, p.bl, p.r))
                                * (d1 + 1)
                                * yref[d1 + 1][d2 - 1];
            }

            fref[d1][d2] -= tau((d2*1.0)/(gsize*1.0), p.ktau, p.a, p.kc, p.x0c, p.bl, p.r)
                            * C((d2*1.0)/(gsize*1.0), p.kc, p.x0c, p.bl, p.r)
                            * d1
                            * yref[d1][d2];
                                
            if (d1 < p.max1-1) {
                fref[d1][d2] += tau((d2*1.0)/(gsize+1.0), p.ktau, p.a, p.kc, p.x0c, p.bl, p.r)
                            * C((d2*1.0)/(gsize+1), p.kc, p.x0c, p.bl, p.r)
                            * (d1+1)
                            * yref[d1+1][d2]; 
                }            
        }
        if (d1==p.max1-1 && d2==p.max2-1) fref[d1][d2] = R_costDeath;
      }
    }


    return GSL_SUCCESS;

} //********** end function dydt definition ********************************************************

#endif // DYN_DIFF_HPP_INCLUDED
