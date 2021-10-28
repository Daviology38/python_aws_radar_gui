import tkinter as tk
import tkinter.font as tkFont
from aws_radar_get_data import get_data
from aws_radar_plot_data import plot_data
import pyart
from PIL import Image, ImageTk
import os
import re
from tkinter import filedialog
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import metpy.plots as mpplots
import gc
import tempfile
from scipy import spatial

global coords

class App:
    def __init__(self, root):
        # setting title
        root.title("AWS NEXRAD LEVEL 2 GUI")
        # setting window size
        width = 1200
        height = 800
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = "%dx%d+%d+%d" % (
            width,
            height,
            (screenwidth - width) / 4,
            (screenheight - height) / 4,
        )
        root.geometry(alignstr)
        root.resizable(width=False, height=False)
        root.configure(bg="white")

        self.img = None
        datevar = tk.StringVar()
        datevar.set("mmddyyyy")
        starttimevar = tk.StringVar()
        starttimevar.set("hh")
        endtimevar = tk.StringVar()
        endtimevar.set("hh")
        stat = tk.StringVar()
        stat.set("KBOX")
        self.index = 0
        self.photo = None
        self.imagelist = []
        self.maxind = 0
        self.gif = None
        self.station = None

        def new_map(fig, lon=-98.6, lat=39.8):
            # Create projection centered on the radar. This allows us to use x
            # and y relative to the radar.
            proj = ccrs.LambertConformal(central_longitude=lon, central_latitude=lat)

            # New axes with the specified projection
            ax = fig.add_axes([0.02, 0.02, 0.96, 0.96], projection=proj)

            # Add coastlines and states
            ax.add_feature(cfeature.COASTLINE.with_scale("50m"), linewidth=2)
            ax.add_feature(cfeature.STATES.with_scale("50m"))

            return ax

        self.fig = plt.figure(figsize=(7.5, 7.5))
        self.ax = new_map(self.fig)

        # Set limits in lat/lon space
        self.ax.set_extent([-135, -65, 22, 50])

        self.ax.add_feature(cfeature.OCEAN.with_scale("50m"))
        self.ax.add_feature(cfeature.LAND.with_scale("50m"))

        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="x")
        self.canvas.get_tk_widget().place(x=80, y=30, width=1000, height=600)

        def savefile():

            filename = filedialog.asksaveasfile(
                mode="wb",
                defaultextension=".png",
                filetypes=(("PNG file", "*.png"), ("All Files", "*.*")),
            )
            if not filename:
                return
            else:
                self.fig.savefig(filename)

        def savegif():
            count = 0
            if len(self.keys) == 0:
                tk.messagebox.showerror(
                    title="Error", message="Needs an image to be plotted to save!"
                )
            else:
                temp_dir = tempfile.mkdtemp()

                for i, key in enumerate(self.keys):
                    try:
                        lla, ref, date, lon, lat = plot_data(self.keys[i], self.station)

                        ref_norm, ref_cmap = mpplots.ctables.registry.get_with_steps(
                            "NWSReflectivity", 5, 5
                        )

                        def new_map(fig, lon, lat):
                            # Create projection centered on the radar. This allows us to use x
                            # and y relative to the radar.
                            proj = ccrs.LambertConformal(
                                central_longitude=lon, central_latitude=lat
                            )

                            # New axes with the specified projection
                            ax = fig.add_axes([0.02, 0.02, 0.96, 0.96], projection=proj)

                            # Add coastlines and states
                            ax.add_feature(
                                cfeature.COASTLINE.with_scale("50m"), linewidth=2
                            )
                            ax.add_feature(cfeature.STATES.with_scale("50m"))

                            return ax

                        fig = plt.figure(figsize=(7.5, 7.5))
                        ax = new_map(fig, lon, lat)
                        # Set limits in lat/lon space
                        ax.set_extent([lon - 5, lon + 5, lat - 3, lat + 3])
                        ax.add_feature(cfeature.OCEAN.with_scale("50m"))
                        ax.add_feature(cfeature.LAND.with_scale("50m"))

                        mesh = ax.pcolormesh(
                            lla[0][:],
                            lla[1][:],
                            ref,
                            cmap=ref_cmap,
                            norm=ref_norm,
                            transform=ccrs.PlateCarree(),
                            zorder=1,
                        )

                        text = ax.text(
                            0.7,
                            0.02,
                            date,
                            transform=self.ax.transAxes,
                            fontdict={"size": 10},
                            bbox=dict(
                                facecolor="white",
                                edgecolor="white",
                                boxstyle="round,pad=0.3",
                            ),
                        )
                        plt.colorbar(mesh, ax=ax, shrink=0.72, label="dBZ")
                        plt.savefig(temp_dir + "/" + str(count) + ".png")
                        plt.close()
                        gc.collect()
                        del mesh
                        del ref
                        del lla
                        count += 1
                    except:
                        count += 1
                imagelist = os.listdir(temp_dir)
                img, *imgs = [Image.open(temp_dir + "/" + f) for f in imagelist]
                filename = filedialog.asksaveasfile(
                    mode="wb",
                    defaultextension=".gif",
                    filetypes=(("GIF file", "*.gif"), ("All Files", "*.*")),
                )
                img.save(
                    fp=filename,
                    format="GIF",
                    append_images=imgs,
                    save_all=True,
                    duration=1000,
                    loop=0,
                )

        # function to open a new window
        # on a button click

        def openNewWindow(self):
            def new_map(fig, lon=-98.6, lat=39.8):
                # Create projection centered on the radar. This allows us to use x
                # and y relative to the radar.
                proj = ccrs.LambertConformal(
                    central_longitude=lon, central_latitude=lat
                )

                # New axes with the specified projection
                ax = fig.add_axes([0.02, 0.02, 0.96, 0.96], projection=proj)

                # Add coastlines and states
                ax.add_feature(cfeature.COASTLINE.with_scale("50m"), linewidth=2)
                ax.add_feature(cfeature.STATES.with_scale("50m"))

                return ax

            # Toplevel object which will
            # be treated as a new window
            newWindow = tk.Toplevel(root)

            # sets the title of the
            # Toplevel widget
            newWindow.title("Station Choice")

            # sets the geometry of toplevel
            width = 1072
            height = 668
            screenwidth = root.winfo_screenwidth()
            screenheight = root.winfo_screenheight()
            alignstr = "%dx%d+%d+%d" % (
                width,
                height,
                (screenwidth - width) / 2,
                (screenheight - height) / 2,
            )
            newWindow.geometry(alignstr)

            # A Label widget to show in toplevel

            fig = plt.figure(figsize=(7.5, 7.5))
            ax = new_map(fig)

            # Set limits in lat/lon space
            ax.set_extent([-135, -65, 22, 50])

            ax.add_feature(cfeature.OCEAN.with_scale("50m"))
            ax.add_feature(cfeature.LAND.with_scale("50m"))

            canvas = FigureCanvasTkAgg(fig, master=newWindow)  # A tk.DrawingArea.
            canvas.draw()
            canvas.get_tk_widget().pack()

            global coords
            coords = []

            def onclick(event):
                global ix, iy
                ix, iy = event.xdata, event.ydata

                def coordXform(orig_crs, target_crs, x, y):
                    return target_crs.transform_point(x, y, orig_crs)

                ix, iy = coordXform(
                    ccrs.LambertConformal(
                        central_longitude=-98.6, central_latitude=39.8
                    ),
                    ccrs.PlateCarree(),
                    ix,
                    iy,
                )

                coords.append((ix, iy))

                if len(coords) == 1:
                    fig.canvas.mpl_disconnect(cid)
                    newWindow.destroy()

            cid = fig.canvas.mpl_connect("button_press_event", onclick)

        button = tk.Button(root, text="save as", command=savefile)
        button.pack()
        button.place(x=0, y=0, width=80, height=25)

        button = tk.Button(root, text="make gif", command=savegif)
        button.pack()
        button.place(x=90, y=0, width=80, height=25)

        # Create Dropdown menu
        locs = pyart.io.nexrad_common.NEXRAD_LOCATIONS
        stationlist = tk.Button(
            root, text="Pick radar location", command=lambda: openNewWindow(self)
        )
        stationlist.pack()
        # Populate the listbox with radar locations
        stationlist["borderwidth"] = "1px"
        ft = tkFont.Font(family="Times", size=10)
        stationlist["font"] = ft
        stationlist["fg"] = "#333333"
        stationlist["justify"] = "center"
        stationlist.place(x=280, y=700, width=120, height=25)

        date = tk.Entry(root, textvariable=datevar)
        date["borderwidth"] = "1px"
        ft = tkFont.Font(family="Times", size=10)
        date.place(x=430, y=700, width=70, height=25)

        starttime = tk.Entry(root, textvariable=starttimevar)
        starttime["borderwidth"] = "1px"
        ft = tkFont.Font(family="Times", size=10)
        starttime["font"] = ft
        starttime["fg"] = "#333333"
        starttime["justify"] = "center"
        starttime["text"] = "Start Hour"
        starttime.place(x=520, y=700, width=70, height=25)

        endtime = tk.Entry(root, textvariable=endtimevar)
        endtime["borderwidth"] = "1px"
        ft = tkFont.Font(family="Times", size=10)
        endtime["font"] = ft
        endtime["fg"] = "#333333"
        endtime["justify"] = "center"
        endtime["text"] = "End Hour"
        endtime.place(x=610, y=700, width=70, height=25)

        GButton_132 = tk.Button(
            root,
            command=lambda: self.GButton_132_command(
                stat.get(), date.get(), starttime.get(), endtime.get()
            ),
        )
        GButton_132["bg"] = "#f0f0f0"
        ft = tkFont.Font(family="Times", size=10)
        GButton_132["font"] = ft
        GButton_132["fg"] = "#000000"
        GButton_132["justify"] = "center"
        GButton_132["text"] = "Submit"
        GButton_132.place(x=700, y=700, width=70, height=25)

        forward = tk.Button(root, command=lambda: self.forward_command(self.index))
        forward["bg"] = "#f0f0f0"
        ft = tkFont.Font(family="Times", size=10)
        forward["font"] = ft
        forward["fg"] = "#000000"
        forward["justify"] = "center"
        forward["text"] = "->"
        forward.place(x=560, y=650, width=70, height=25)

        back = tk.Button(root, command=lambda: self.back_command(self.index))
        back["bg"] = "#f0f0f0"
        ft = tkFont.Font(family="Times", size=10)
        back["font"] = ft
        back["fg"] = "#000000"
        back["justify"] = "center"
        back["text"] = "<-"
        back.place(x=470, y=650, width=70, height=25)

    def back_command(self, index):
        self.index -= 1
        if self.index < 0:
            self.index = len(self.keys) - 1
        try:
            lla, ref, date, lon, lat = plot_data(self.keys[self.index], self.station)
            self.ax.clear()
            self.fig.clf()
            ref_norm, ref_cmap = mpplots.ctables.registry.get_with_steps(
                "NWSReflectivity", 5, 5
            )

            def new_map(fig, lon, lat):
                # Create projection centered on the radar. This allows us to use x
                # and y relative to the radar.
                proj = ccrs.LambertConformal(central_longitude=lon, central_latitude=lat)

                # New axes with the specified projection
                ax = fig.add_axes([0.02, 0.02, 0.96, 0.96], projection=proj)

                # Add coastlines and states
                ax.add_feature(cfeature.COASTLINE.with_scale("50m"), linewidth=2)
                ax.add_feature(cfeature.STATES.with_scale("50m"))

                return ax

            self.ax = new_map(self.fig, lon, lat)
            # Set limits in lat/lon space
            self.ax.set_extent([lon - 5, lon + 5, lat - 3, lat + 3])
            self.ax.add_feature(cfeature.OCEAN.with_scale("50m"))
            self.ax.add_feature(cfeature.LAND.with_scale("50m"))

            mesh = self.ax.pcolormesh(
                lla[0][:],
                lla[1][:],
                ref,
                cmap=ref_cmap,
                norm=ref_norm,
                transform=ccrs.PlateCarree(),
                zorder=1,
            )

            text = self.ax.text(
                0.7,
                0.02,
                date,
                transform=self.ax.transAxes,
                fontdict={"size": 10},
                bbox=dict(facecolor="white", edgecolor="white", boxstyle="round,pad=0.3"),
            )
            plt.colorbar(mesh, ax=self.ax, shrink=0.72, label="dBZ")
            self.canvas.draw()
            gc.collect()
            del ref
            del lla
            del mesh
        except:
            self.back_command(self.index)

    def forward_command(self, index):
        self.index += 1
        if self.index == len(self.keys):
            self.index = 0
        try:
            lla, ref, date, lon, lat = plot_data(self.keys[self.index], self.station)
            self.ax.clear()
            self.fig.clf()
            ref_norm, ref_cmap = mpplots.ctables.registry.get_with_steps(
                "NWSReflectivity", 5, 5
            )

            def new_map(fig, lon, lat):
                # Create projection centered on the radar. This allows us to use x
                # and y relative to the radar.
                proj = ccrs.LambertConformal(central_longitude=lon, central_latitude=lat)

                # New axes with the specified projection
                ax = fig.add_axes([0.02, 0.02, 0.96, 0.96], projection=proj)

                # Add coastlines and states
                ax.add_feature(cfeature.COASTLINE.with_scale("50m"), linewidth=2)
                ax.add_feature(cfeature.STATES.with_scale("50m"))

                return ax

            self.ax = new_map(self.fig, lon, lat)
            # Set limits in lat/lon space
            self.ax.set_extent([lon - 5, lon + 5, lat - 3, lat + 3])
            self.ax.add_feature(cfeature.OCEAN.with_scale("50m"))
            self.ax.add_feature(cfeature.LAND.with_scale("50m"))

            mesh = self.ax.pcolormesh(
                lla[0][:],
                lla[1][:],
                ref,
                cmap=ref_cmap,
                norm=ref_norm,
                transform=ccrs.PlateCarree(),
                zorder=1,
            )

            text = self.ax.text(
                0.7,
                0.02,
                date,
                transform=self.ax.transAxes,
                fontdict={"size": 10},
                bbox=dict(facecolor="white", edgecolor="white", boxstyle="round,pad=0.3"),
            )
            plt.colorbar(mesh, ax=self.ax, shrink=0.72, label="dBZ")
            self.canvas.draw()
            gc.collect()
            del mesh
            del ref
            del lla
        except:
            self.forward_command(self.index)

    def GButton_132_command(self, stat, dat, st, et):
        # Check to see if text is changed
        if (len(et) != 2) or (len(st) != 2):
            tk.messagebox.showerror(
                title="Error",
                message="Wrong Format! Make sure hour is 2 digits e.g. 00 or 12",
            )
            y = 0
            z = 0
        elif int(et) < int(st):
            tk.messagebox.showerror(
                title="Error",
                message="Mamma Mia! The end time must be after the start time!",
            )
            y = 0
            z = 0
        else:
            y = 1
        if len(dat) != 8:
            tk.messagebox.showerror(
                title="Error",
                message="Wrong Format! Make sure date is 8 digits e.g. 08312021",
            )
            y = 0
            z = 0
        else:
            z = 1
        if len(coords) == 0:
            y = 0
            z = 0
            tk.messagebox.showerror(
                title="Error", message="Need to pick a Lat Lon point for a station!"
            )
        else:
            y = 1
            z = 1
        if y == 1 and z == 1:
            locs = pyart.io.nexrad_common.NEXRAD_LOCATIONS
            locs2 = [loc for loc in locs if loc[0] == "T"]
            for unwanted_key in locs2: del locs[unwanted_key]

            vals = [(locs[l]['lat'], locs[l]['lon']) for l in locs]
            tree = spatial.KDTree(vals)
            v, ind = tree.query([(coords[0][1], coords[0][0])])
            self.station = list(locs.keys())[ind[0]]

            self.keys = get_data(self.station, dat, st, et)
            lla, ref, date, lon, lat = plot_data(self.keys[self.index], self.station)

            self.ax.clear()
            self.fig.clf()
            ref_norm, ref_cmap = mpplots.ctables.registry.get_with_steps(
                "NWSReflectivity", 5, 5
            )

            def new_map(fig, lon, lat):
                # Create projection centered on the radar. This allows us to use x
                # and y relative to the radar.
                proj = ccrs.LambertConformal(
                    central_longitude=lon, central_latitude=lat
                )

                # New axes with the specified projection
                ax = fig.add_axes([0.02, 0.02, 0.96, 0.96], projection=proj)

                # Add coastlines and states
                ax.add_feature(cfeature.COASTLINE.with_scale("50m"), linewidth=2)
                ax.add_feature(cfeature.STATES.with_scale("50m"))

                return ax

            self.ax = new_map(self.fig, lon, lat)
            # Set limits in lat/lon space
            self.ax.set_extent([lon - 5, lon + 5, lat - 3, lat + 3])
            self.ax.add_feature(cfeature.OCEAN.with_scale("50m"))
            self.ax.add_feature(cfeature.LAND.with_scale("50m"))

            mesh = self.ax.pcolormesh(
                lla[0][:],
                lla[1][:],
                ref,
                cmap=ref_cmap,
                norm=ref_norm,
                transform=ccrs.PlateCarree(),
                zorder=1,
            )

            text = self.ax.text(
                0.7,
                0.02,
                date,
                transform=self.ax.transAxes,
                fontdict={"size": 10},
                bbox=dict(
                    facecolor="white", edgecolor="white", boxstyle="round,pad=0.3"
                ),
            )
            plt.colorbar(mesh, ax=self.ax, shrink=0.72, label="dBZ")
            self.canvas.draw()
            gc.collect()
            del ref
            del lla
            del mesh

        else:
            tk.messagebox.showerror(title="Error", message="Try Again!")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
