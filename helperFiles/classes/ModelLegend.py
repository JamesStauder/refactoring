from pyqtgraph import LegendItem, LabelItem
from pyqtgraph.graphicsItems.LegendItem import ItemSample

'''
Class: ModelLegend
Argument list: 
size - Size of Legend
offset - offset of Legend
Purpose: These are the legends for the model plotter
Dependencies: pyqtgraph LegendItem, LabelItem, ItemSample
Creator: Patrick Kreitzberg
Date created: Unknown
Last edited: 3/9/18
'''


class ModelLegend(LegendItem):
    def __init__(self, size=None, offset=None):
        LegendItem.__init__(self, size, offset)

    def addItem(self, item, name):
        """
        Add a new entry to the legend.

        ==============  ========================================================
        **Arguments:**
        item            A PlotDataItem from which the line and point style
                        of the item will be determined or an instance of
                        ItemSample (or a subclass), allowing the item display
                        to be customized.
        title           The title to display for this item. Simple HTML allowed.
        ==============  ========================================================
        """
        label = LabelItem(name, color=(0, 0, 0))
        if isinstance(item, ItemSample):
            sample = item
        else:
            sample = ItemSample(item)
        row = self.layout.rowCount()
        self.items.append((sample, label))
        self.layout.addItem(sample, row, 0)
        self.layout.addItem(label, row, 1)
        self.updateSize()