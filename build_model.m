function build_model(model_name, fpga_type)
    model = generate_model(model_name, fpga_type);
    t0 = datetime;
    a = jasper_frontend(model); system([a ' --jobs 12'])
    t1 = datetime;
    build_duration = t1 - t0;
    sprintf('Build ended after duration %s', build_duration);
end
