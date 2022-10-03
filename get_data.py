import ifcopenshell
import json
import os

def ifc_to_json(folder: String ="."):
    found = False

    for path, curr_dir, files in os.walk(folder):
        for file in files:
            if not file.endswith(".ifc"):
                continue

            found = True
            print(path + "/" + file)
            ifc = ifcopenshell.open(path + "/" + file)
            res = {}
            for part in ifc:
                try:
                    data = get_all_instance_data(part)
                    if not data:
                        continue
                    res[part.id()] = data
                except:
                    pass

            file = file.replace(".ifc", "")
            with open(f"{path}/{file}_data.json", "w", encoding="utf-8") as f:
                json.dump(res, f, indent=4, ensure_ascii=False)


def get_all_instance_data(ifc_instance):

    pset_dict= {}
    
    #getting pset single values
    {pset_dict.update(get_property_single_value(x))\
     for x in get_related_property_sets(ifc_instance)}

    #getting basequantities single values
    {pset_dict.update(get_quantity_single_value(x)) \
     for x in get_related_quantities(ifc_instance)}

    #getting type
    {pset_dict.update(get_type_single_value(x)) \
     for x in get_related_type_definition(ifc_instance)}

    return pset_dict


def get_property_single_value(x):
    attributes_dicts = {}
    for y in x.HasProperties:
        if y.is_a("IfcPropertySingleValue") and y.NominalValue is not None:
            attributes_dicts.update({y.Name:y.NominalValue.wrappedValue})
        if y.is_a("IfcComplexProperty"):
            for z in y.HasProperties:
                if z.NominalValue is not None:
                    attributes_dicts.update({z.Name: z.NominalValue.wrappedValue})

    return attributes_dicts


def get_related_property_sets(ifc_instance):
    properties_list = []

    for x in ifc_instance.IsDefinedBy:
        if x.is_a("IfcRelDefinesByProperties"):
            if x.RelatingPropertyDefinition.is_a("IfcPropertySet"):
                properties_list.append(x.RelatingPropertyDefinition)
    return properties_list      


def get_quantity_single_value(x):
    quantities_dicts = {}

    for y in x.Quantities:
        if y.is_a('IfcQuantityArea'):
            quantities_dicts.update({y.Name:y.AreaValue})
        if y.is_a('IfcQuantityLength'):
            quantities_dicts.update({y.Name:y.LengthValue})
        if y.is_a('IfcQuantityVolume'):
            quantities_dicts.update({y.Name:y.VolumeValue})
        if y.is_a('IfcQuantityCount'):
            quantities_dicts.update({y.Name:y.CountValue})
        if y.is_a('IfcQuantityWeight'):
            quantities_dicts.update({y.Name:y.WeightValue})
        
    return quantities_dicts


def get_related_quantities(ifc_instance):
    quantities_list = []

    for x in ifc_instance.IsDefinedBy:
        if x.is_a("IfcRelDefinesByProperties"):
            if x.RelatingPropertyDefinition.is_a("IfcElementQuantity"):
                quantities_list.append(x.RelatingPropertyDefinition)
    return quantities_list


def get_type_single_value(x):

    type_attr_dicts = {}

    if x.HasPropertySets:
        try:
            {type_attr_dicts.update({"TypeDefinition_" + x.Name:y.Name}) for y in x.HasPropertySets if y.Name is not None}
        except:
            print("Type Value Exception for IfcGlobalID "+ x.GlobalId)

    return type_attr_dicts 


def get_related_type_definition(ifc_instance):
    defined_by_type_list=[x.RelatingType for x in ifc_instance.IsDefinedBy \
                          if x.is_a("IfcRelDefinesByType")]
    return defined_by_type_list


if __name__ == "__main__":
    ifc_to_json()
