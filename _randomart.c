#include <stdint.h>
#include <math.h>
#include <stdio.h>


struct qcolor {
    double r;
    double g;
    double b;
};


struct transforminfo {
    struct qcolor (* apply)(struct transforminfo *info, double x, double y);
    int (* inspect)(struct transforminfo *info, char *buf, size_t buflen);
    struct transforminfo* subslots[4];
    char data[80];
};


struct ra_constant_data {
    double channels[3];
};



// struct ra_product_data {
//     struct transforminfo* e1;
//     struct transforminfo* e2;
// };


struct ra_sin_data {
    double phase;
    double freq;
};


struct ra_level_data {
    double threshold;
};


inline double well(double x) {
    return 1.0 - 2.0 / pow(1 + x * x, 8);
}


inline double tent(double x) {
    return 1.0 - 2.0 * abs(x);
}


struct qcolor ra_transforminfo_apply(struct transforminfo *info, double x, double y) {
    return info->apply(info, x, y);
}


void qcolor_average(struct qcolor c1, struct qcolor c2, double weight, struct qcolor *output) {
    output->r = weight * c1.r + (1 - weight) * c2.r;
    output->g = weight * c1.g + (1 - weight) * c2.g;
    output->b = weight * c1.b + (1 - weight) * c2.b;
}


void qcolor_tent(struct qcolor c1, struct qcolor *output) {
    output->r = tent(c1.r);
    output->g = tent(c1.g);
    output->b = tent(c1.b);
}


void qcolor_well(struct qcolor c1, struct qcolor *output) {
    output->r = well(c1.r);
    output->g = well(c1.g);
    output->b = well(c1.b);
}


void qcolor_product(struct qcolor c1, struct qcolor c2, struct qcolor *output) {
    output->r = c1.r * c2.r;
    output->g = c1.g * c2.g;
    output->b = c1.b * c2.b;
}


void qcolor_mod(struct qcolor c1, struct qcolor c2, struct qcolor *output) {
    double zeroish = 0.0001;
    if ((c2.r < zeroish) || (c2.g < zeroish) || (c2.b < zeroish)) {
        output->r = 0.0;
        output->g = 0.0;
        output->b = 0.0;
    } else {
        output->r = fmod(c1.r, c2.r);
        output->g = fmod(c1.g, c2.g);
        output->b = fmod(c1.b, c2.b);
    }
}


void qcolor_sin(struct qcolor c, double phase, double freq, struct qcolor *out) {
    out->r = sin(phase + freq * c.r);
    out->g = sin(phase + freq * c.g);
    out->b = sin(phase + freq * c.b);
}


void qcolor_level(
    double threshold, struct qcolor c1,
    struct qcolor c2, struct qcolor c3,
    struct qcolor *out
) {
    out->r = c1.r < threshold ? c2.r : c3.r;
    out->g = c1.g < threshold ? c2.g : c3.g;
    out->b = c1.b < threshold ? c2.b : c3.b;
}


struct qcolor ra_variable_x(struct transforminfo *info, double x, double y) {
    struct qcolor out;
    out.r = x;
    out.g = x;
    out.b = x;
    return out;
}


int ra_variable_x_inspect(struct transforminfo *info, char *buf, size_t buflen) {
    return snprintf(buf, buflen, "ra_variable_x()");
}


void ra_variable_x_init(struct transforminfo *info) {
    info->apply = &ra_variable_x;
    info->inspect = &ra_variable_x_inspect;
}


struct qcolor ra_variable_y(struct transforminfo *info, double x, double y) {
    struct qcolor out;
    out.r = y;
    out.g = y;
    out.b = y;
    return out;
}


int ra_variable_y_inspect(struct transforminfo *info, char *buf, size_t buflen) {
    return snprintf(buf, buflen, "ra_variable_y()");
}


void ra_variable_y_init(struct transforminfo *info) {
    info->apply = &ra_variable_y;
    info->inspect = &ra_variable_y_inspect;
}


struct qcolor ra_constant(struct transforminfo *info, double x, double y) {
    struct ra_constant_data *data = (struct ra_constant_data*) info->data;
    struct qcolor out;
    out.r = data->channels[0];
    out.g = data->channels[1];
    out.b = data->channels[2];
    return out;
}


int ra_constant_inspect(struct transforminfo *info, char *buf, size_t buflen) {
    struct ra_constant_data *data = (struct ra_constant_data*) info->data;

    return snprintf(buf, buflen, "ra_constant(r=%f, g=%f, b=%f)",
        data->channels[0], data->channels[1], data->channels[2]);
}


void ra_constant_init(struct transforminfo *info, double r, double g, double b) {
    struct ra_constant_data *data = (struct ra_constant_data*) info->data;

    info->apply = &ra_constant;
    info->inspect = &ra_constant_inspect;
    data->channels[0] = r;
    data->channels[1] = g;
    data->channels[2] = b;
}


struct qcolor ra_sum(struct transforminfo *info, double x, double y) {
    struct qcolor c1 = ra_transforminfo_apply(info->subslots[0], x, y);
    struct qcolor c2 = ra_transforminfo_apply(info->subslots[1], x, y);
    
    struct qcolor out;
    qcolor_average(c1, c2, 0.5f, &out);
    return out;
}


int ra_sum_inspect(struct transforminfo *info, char *buf, size_t buflen) {
    return snprintf(buf, buflen, "ra_sum(..., ...)");
}


void ra_sum_init(
    struct transforminfo *info,
    struct transforminfo *e1,
    struct transforminfo *e2
) {
    info->apply = &ra_sum;
    info->inspect = &ra_sum_inspect;
    info->subslots[0] = e1;
    info->subslots[1] = e2;
}


struct qcolor ra_product(struct transforminfo *info, double x, double y) {
    struct ra_product_data *data = (struct ra_product_data*) info->data;
    struct qcolor c1 = ra_transforminfo_apply(info->subslots[0], x, y);
    struct qcolor c2 = ra_transforminfo_apply(info->subslots[1], x, y);
    struct qcolor out;
    qcolor_product(c1, c2, &out);
    return out;
}


int ra_product_inspect(struct transforminfo *info, char *buf, size_t buflen) {
    return snprintf(buf, buflen, "ra_product(..., ...)");
}


void ra_product_init(
    struct transforminfo *info,
    struct transforminfo *e1,
    struct transforminfo *e2
) {
    struct ra_product_data *data = (struct ra_product_data*) info->data;

    info->apply = &ra_product;
    info->inspect = &ra_product_inspect;
    info->subslots[0] = e1;
    info->subslots[1] = e2;
}


struct qcolor ra_mod(struct transforminfo *info, double x, double y) {
    struct qcolor c1 = ra_transforminfo_apply(info->subslots[0], x, y);
    struct qcolor c2 = ra_transforminfo_apply(info->subslots[1], x, y);
    struct qcolor out;
    qcolor_mod(c1, c2, &out);
    return out;
}


int ra_mod_inspect(struct transforminfo *info, char *buf, size_t buflen) {
    return snprintf(buf, buflen, "ra_mod(..., ...)");
}


void ra_mod_init(
    struct transforminfo *info,
    struct transforminfo *e1,
    struct transforminfo *e2
) {
    info->apply = &ra_mod;
    info->inspect = &ra_mod_inspect;
    info->subslots[0] = e1;
    info->subslots[1] = e2;
}


struct qcolor ra_well(struct transforminfo *info, double x, double y) {
    struct qcolor c1 = ra_transforminfo_apply(info->subslots[0], x, y);
    struct qcolor out;
    qcolor_well(c1, &out);
    return out;
}


int ra_well_inspect(struct transforminfo *info, char *buf, size_t buflen) {
    return snprintf(buf, buflen, "ra_well(...)");
}


void ra_well_init(
    struct transforminfo *info,
    struct transforminfo *e1
) {
    info->apply = &ra_well;
    info->inspect = &ra_well_inspect;
    info->subslots[0] = e1;
}


struct qcolor ra_tent(struct transforminfo *info, double x, double y) {
    struct qcolor c1 = ra_transforminfo_apply(info->subslots[0], x, y);
    struct qcolor out;
    qcolor_tent(c1, &out);
    return out;
}


int ra_tent_inspect(struct transforminfo *info, char *buf, size_t buflen) {
    return snprintf(buf, buflen, "ra_tent(...)");
}


void ra_tent_init(
    struct transforminfo *info,
    struct transforminfo *e1
) {
    info->apply = &ra_tent;
    info->inspect = &ra_tent_inspect;
    info->subslots[0] = e1;
}


struct qcolor ra_sin(struct transforminfo *info, double x, double y) {
    struct qcolor c1 = ra_transforminfo_apply(info->subslots[0], x, y);
    struct ra_sin_data *data = (struct ra_sin_data*) info->data;
    struct qcolor out;
    qcolor_sin(c1, data->phase, data->freq, &out);
    return out;
}


int ra_sin_inspect(struct transforminfo *info, char *buf, size_t buflen) {
    struct ra_sin_data *data = (struct ra_sin_data*) info->data;
    return snprintf(buf, buflen, "ra_sin(phase=%f, freq=%f, ...)", data->phase, data->freq);
}


void ra_sin_init(
    struct transforminfo *info,
    double phase,
    double freq,
    struct transforminfo *e1
) {
    struct ra_sin_data *data = (struct ra_sin_data*) info->data;

    info->apply = &ra_sin;
    info->inspect = &ra_sin_inspect;
    info->subslots[0] = e1;
    data->phase = phase;
    data->freq = freq;
}


struct qcolor ra_level(struct transforminfo *info, double x, double y) {
    struct qcolor levelc = ra_transforminfo_apply(info->subslots[0], x, y);
    struct qcolor c1 = ra_transforminfo_apply(info->subslots[1], x, y);
    struct qcolor c2 = ra_transforminfo_apply(info->subslots[2], x, y);

    struct ra_level_data *data = (struct ra_level_data*) info->data;
    struct qcolor out;
    qcolor_level(data->threshold, levelc, c1, c2, &out);
    return out;
}


int ra_level_inspect(struct transforminfo *info, char *buf, size_t buflen) {
    struct ra_level_data *data = (struct ra_level_data*) info->data;
    return snprintf(buf, buflen, "ra_level(..., threshold=%f)", data->threshold);
}


void ra_level_init(
    struct transforminfo *info,
    double threshold,
    struct transforminfo *level,
    struct transforminfo *e1,
    struct transforminfo *e2
) {
    struct ra_level_data *data = (struct ra_level_data*) info->data;

    info->apply = &ra_level;
    info->inspect = &ra_level_inspect;
    info->subslots[0] = level;
    info->subslots[1] = e1;
    info->subslots[2] = e2;
    data->threshold = threshold;
}


struct qcolor ra_mix(struct transforminfo *info, double x, double y) {
    struct qcolor wc = ra_transforminfo_apply(info->subslots[0], x, y);
    struct qcolor c1 = ra_transforminfo_apply(info->subslots[1], x, y);
    struct qcolor c2 = ra_transforminfo_apply(info->subslots[2], x, y);

    struct qcolor out;
    qcolor_average(c1, c2, 0.5 * (wc.r + 1.0), &out);
    return out;
}


int ra_mix_inspect(struct transforminfo *info, char *buf, size_t buflen) {
    return snprintf(buf, buflen, "ra_mix(..., ..., ...)");
}


void ra_mix_init(
    struct transforminfo *info,
    struct transforminfo *w,
    struct transforminfo *e1,
    struct transforminfo *e2
) {
    info->apply = &ra_mix;
    info->inspect = &ra_mix_inspect;
    info->subslots[0] = w;
    info->subslots[1] = e1;
    info->subslots[2] = e2;
}