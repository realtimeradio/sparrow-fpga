function new_model = generate_model(model_name, fpga_type)
    % Check:
    %   - FPGA is an allowed model
    %   - input file exists
    %   - output file doesn't exist.
    allowed_fpgas = {'xc7z030', 'xc7z035', 'xc7z045'};
    if ~exist(model_name, 'file')
        error('Model %s does not exist!', model_name);
    end
    if ~any(matches(allowed_fpgas, fpga_type))
        allowed_fpgas
        error('FPGA type %s is not allowed.', fpga_type);
    end
    [filepath, name, ext] = fileparts(model_name);
    new_model = [filepath '/' name '_' fpga_type];
    if exist([new_model '.slx'], 'file')
        error('Model %s already exists', new_model);
    end
    % Open input model. Change FPGA type and save as new file.
    % return system name.
    open_system(model_name);
    set_param([name '/SPARROW'], 'hw_sys', ['SPARROW:' fpga_type]);
    save_system(name, new_model);
    close_system(new_model);
end
