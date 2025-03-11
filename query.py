results = (
        db.query(
            Request.first_name,
            Request.last_name,
            Request.recipient_email,
            Request.requester_email,
            Request.phone_number,
            Device.device_name,
            Device.device_model,
            Device.device_type,
            Device.device_id
        )
        .join(
            Device,
            cast(
                func.regexp_replace(
                    func.split_part(Request.device_quantities, ':', 1),
                    '[^0-9]',
                    '',
                    'g'
                ), 
                Integer
            ) == Device.device_id
        )
        .all()
    )


SELECT
    device_os,
    REPLACE(device_name, ' ', '') AS device_name,
    REPLACE(device_model, ' ', '') AS device_model
FROM
    devices;

