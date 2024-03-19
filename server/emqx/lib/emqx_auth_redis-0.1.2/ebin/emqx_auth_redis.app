{application,emqx_auth_redis,
             [{description,"EMQX Redis Authentication and Authorization"},
              {vsn,"0.1.2"},
              {registered,[]},
              {mod,{emqx_auth_redis_app,[]}},
              {applications,[kernel,stdlib,emqx,emqx_redis,emqx_auth]},
              {env,[]},
              {modules,[emqx_auth_redis_app,emqx_auth_redis_sup,
                        emqx_auth_redis_validations,emqx_authn_redis,
                        emqx_authn_redis_schema,emqx_authz_redis,
                        emqx_authz_redis_schema]},
              {licenses,["Apache 2.0"]},
              {links,[]}]}.