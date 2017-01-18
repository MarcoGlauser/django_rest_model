from rest_framework.utils import model_meta


def create_instance(ModelClass, validated_data, using=None):
    """
    Thanks to Django DRF for providing this.
    The problem is that Model.objects.create(**validated_data) automatically saves the model and therefore creates an infinite loop :(
    """

    # Remove many-to-many relationships from validated_data.
    # They are not valid arguments to the default `.create()` method,
    # as they require that the instance has already been saved.
    # info = model_meta.get_field_info(ModelClass)
    # many_to_many = {}
    # for field_name, relation_info in info.relations.items():
    #     if relation_info.to_many and (field_name in validated_data):
    #         many_to_many[field_name] = validated_data.pop(field_name)

    try:
        instance = ModelClass(**validated_data)
        instance._state.adding = False
        instance._state.db = using
    except TypeError as exc:
        msg = (
            'Got a `TypeError` when calling `%s.objects.create()`. '
            'This may be because you have a writable field on the '
            'serializer class that is not a valid argument to '
            '`%s.objects.create()`. You may need to make the field '
            'read-only, or override the asdf method to handle '
            'this correctly.\nOriginal exception text was: %s.' %
            (
                ModelClass.__name__,
                ModelClass.__name__,
                exc
            )
        )
        raise TypeError(msg)

    # Save many-to-many relationships after the instance is created.
    # kind of a work around since the received elements are from remote they need to appear like already in the db
    # if many_to_many:
    #     for field_name, value in many_to_many.items():
    #         for asdf in value:
    #             asdf._state.adding = False
    #             asdf._state.db = using
    #         setattr(instance, field_name, value)
    #

    return instance