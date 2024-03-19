{application,minirest,
             [{description,"A mini RESTful API framework built on cowboy and swagger"},
              {vsn,"1.3.15"},
              {registered,[]},
              {applications,[kernel,stdlib,cowboy_swagger]},
              {env,[]},
              {modules,[minirest,minirest_api,minirest_binary_encoder,
                        minirest_body,minirest_body_encoder,
                        minirest_file_encoder,minirest_form_data_encoder,
                        minirest_handler,minirest_info_api,
                        minirest_json_encoder,minirest_message_encoder,
                        minirest_trails,minirest_util]},
              {licenses,["Apache 2.0"]},
              {links,["Github","https://github.com/emqx/minirest"]}]}.