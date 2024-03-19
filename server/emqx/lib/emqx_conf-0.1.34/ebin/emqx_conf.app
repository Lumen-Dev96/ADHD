{application,emqx_conf,
             [{description,"EMQX configuration management"},
              {vsn,"0.1.34"},
              {registered,[]},
              {mod,{emqx_conf_app,[]}},
              {applications,[kernel,stdlib,emqx_ctl]},
              {env,[]},
              {modules,[emqx_cluster_rpc,emqx_cluster_rpc_cleaner,emqx_conf,
                        emqx_conf_app,emqx_conf_cli,emqx_conf_proto_v1,
                        emqx_conf_proto_v2,emqx_conf_proto_v3,
                        emqx_conf_schema,emqx_conf_schema_types,
                        emqx_conf_sup]}]}.