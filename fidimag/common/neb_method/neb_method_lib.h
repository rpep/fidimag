#include "math.h"
#define WIDE_PI 3.1415926535897932384626433832795L

void compute_tangents_C(double *ys, double *energy,
                        double *tangents, int image_num, int nodes);

void compute_spring_force_C(double *spring_force,
                            double *y,
                            double *tangents,
                            double k,
                            int n_images,
                            int n_dofs_image
                            );

void project_tangents_C(double *tangents, double *y,
                        int n_images, int n_dofs_image
                        );

void compute_effective_force_C(double * G,
                               double * tangents,
                               double * gradientE,
                               double * spring_force,
                               int n_images,
                               int n_dofs_image);
