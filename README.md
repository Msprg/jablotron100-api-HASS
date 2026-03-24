# jablotron100-api-HASS

Home Assistant integration for the Jablotron API server.

## Install with HACS custom repository

1. In HACS, open the menu for custom repositories.
2. Add `https://github.com/Msprg/jablotron100-api-HASS` as an `Integration`.
3. Install `jablotron100-api-HASS`.
4. Restart Home Assistant.
5. Add the `jablotron100-api-HASS` integration in the UI.

## Configuration

The integration connects to the Jablotron API server instead of talking to the panel over USB directly. The config flow expects:

- `server_url`
- `api_token`
- `tls_ca_cert`
- `tls_client_cert`
- `tls_client_key`

For development, generate a local CA plus server/client certs in the main API server repository with:

```bash
scripts/generate-dev-certs.sh .dev-certs --ip YOUR_SERVER_IP --dns jablotron-api-server.example.lan
```

Then point the config flow at the generated `ca.crt`, `client.crt`, and `client.key` files copied onto the Home Assistant machine.

## Notes

- The integration domain is `jablotron100_api_hass`, so it can be installed alongside the original `jablotron100` integration.
- Section names, PG names, and peripheral metadata are discovered from the API server catalog.
