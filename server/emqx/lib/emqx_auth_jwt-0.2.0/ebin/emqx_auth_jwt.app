{application,emqx_auth_jwt,
             [{description,"EMQX JWT Authentication and Authorization"},
              {vsn,"0.2.0"},
              {registered,[]},
              {mod,{emqx_auth_jwt_app,[]}},
              {applications,[kernel,stdlib,jose,emqx,emqx_auth,emqx_connector,
                             emqx_resource]},
              {env,[]},
              {modules,[emqx_auth_jwt_app,emqx_auth_jwt_sup,
                        emqx_authn_jwks_client,emqx_authn_jwks_connector,
                        emqx_authn_jwt,emqx_authn_jwt_schema]},
              {licenses,["Apache 2.0"]},
              {links,[]}]}.