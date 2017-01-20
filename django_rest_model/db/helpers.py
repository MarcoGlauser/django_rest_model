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

    instance = ModelClass(**validated_data)
    instance._state.adding = False
    instance._state.db = using

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