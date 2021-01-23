import numpy as np

class DeapSettingsHandle:
    def __init__(self, deap_config_ui, df_genes):
        self.deap_config = deap_config_ui # instance of deap_config_ui
        self.checkboxes = self.deap_config.cblist
        self.values = self.deap_config.vallist
        self.df = df_genes

    def attribute_generator(self):
        """
        Format a list from User settings and gene list for DEAP attribute generator.
        Returns a list of attributes with min and max values, depending on if the user marked it as a free
        parameter or not.
        :return: list
        """
        attributes = []
        for key in self.df.index:
            # attributes valid for both blades (pp, ao, div)
            row = self.df.loc[key]
            # if row.blade == 0:
                # state of attribute is true
            if self.checkboxes[key]:
                _min = row.minimum
                _max = row.maximum
            else:
                _min = row.default
                _max = row.default
            attributes.append([_min, _max, row.digits, key])

        return attributes