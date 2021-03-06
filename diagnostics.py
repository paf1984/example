import numpy as np
#import kwiklib
from spikedetekt2.processing import extract_waveform
import matplotlib
#matplotlib.use("svg")
matplotlib.use("pdf")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.gridspec as gridspec
import pickle 
from matplotlib.backends.backend_pdf import PdfPages


#from IPython import embed # For manual debugging


def diagnostics(threshold = None, probe = None,components = None,chunk = None,chunk_detect= None,chunk_threshold=None, chunk_fil=None, chunk_raw=None,prm = None, **extra_params):

    multdetection_times = prm['diagnostics_time_samples']
    s_start = chunk.s_start  # Absolute start of the chunk
    print 's_start ' , s_start

  
    #debug_fd = GlobalVariables['debug_fd']
    
    samplingrate= prm['sample_rate']
    

    chunk_size_less= prm['chunk_size']-prm['chunk_overlap']
#-Parameters['CHUNK_OVERLAP']
#    print 'Parameters: \n', Parameters
   # probefilename = Parameters['PROBE_FILE']
#    print 'chunk_size_less = ', chunk_size_less
#    window_width = 120
#    samples_backward = 60
    window_width = 140
    samples_backward = 70

    #path = Parameters['OUTPUT_DIR']
    for interestpoint in multdetection_times:
        if (interestpoint - chunk_size_less) <= s_start < (interestpoint):
            #print interestpoint_ms, ':\n'
            #debug_fd.write(str(interestpoint_ms)+':\n')
            print 'interestpoint ', interestpoint, ':\n'
            #debug_fd.write(str(interestpoint)+':\n')
             # sampmin = interestpoint - s_start - 3
            sampmin = np.amax([0,interestpoint - s_start - samples_backward])
            sampmax = sampmin + window_width 
            print 'sampmin, sampmax ',sampmin, sampmax
            #embed()

            
            connected_comp_enum = np.zeros_like(chunk_fil)
            j = 0
            debugnextbits = []
            waveslist = []
            for k,indlist in enumerate(components):
                indtemparray = np.array(indlist.items)
                #print k,':',indlist, '\n'
                #print 'indlist.s_start', indlist.s_start
                
                #print indlist.keep_start 
                #print indlist.keep_end 
            
               # print '\n'
               # j = j+1
               # connected_comp_enum[indtemparray[:,0],indtemparray[:,1]] = j
                
               # debug_fd.write(str(k)+': '+'\n')
               # debug_fd.write(str(indlist)+'\n')
               # debug_fd.write('\n') 
               # debug_fd.flush()   
                
                
                if (set(indtemparray[:,0]).intersection(np.arange(int(sampmin),int(sampmax+1))) != set()):
                    nut = set(indtemparray[:,0]).intersection(np.arange(int(sampmin),int(sampmax+1)))
                    print nut
                    #print 'Am I even getting here'
                    #embed()
                    print k,':',indlist, '\n'
                    print '\n'
                    j = j+1
                    connected_comp_enum[indtemparray[:,0],indtemparray[:,1]] = j
                    
                    #debug_fd.write(str(k)+': '+'\n')
                    #debug_fd.write(str(indlist)+'\n')
                    #debug_fd.write('\n') 
                    #debug_fd.flush()       # makes sure everything is written to the debug file as program proceeds
                    
                    
                    #N_CH = prms['nchannels']
                    
                    chunk_extract = chunk_detect 
                    wv = extract_waveform(indlist,
                                 chunk_extract=chunk_extract,
                                 chunk_fil=chunk_fil,
                                 chunk_raw=chunk_raw,
                                 threshold_strong=threshold.strong,
                                 threshold_weak=threshold.weak,
                                 probe=probe,
                                 **prm)
                    
                    
                 
                    s_peak =  wv.sf_offset - wv.s_start
                    sf_peak=  s_peak + wv.s_frac_part
                    print 'wv.s_min', wv.s_min,'\n'
                    print 'wv.s_start', wv.s_start,'\n'
                    print 'wv.sf_offset', wv.sf_offset,'\n'
                    print 'wv.s_frac_part',wv.s_frac_part,'\n'                            
                    debugnextbits.append((s_peak, sf_peak))
                    print 'debugnextbits =', debugnextbits
                    waveslist.append(wv)
                    #debug_fd.write('debugnextbits ='+ str(debugnextbits)+'\n')
                    #debug_fd.flush()  
                    #embed()
            total_height = 4
            total_width = 4
            gs = gridspec.GridSpec(total_height,total_width)
            fig1 = plt.figure()
            #filtchunk_normalised = np.maximum((filteredchunk - ThresholdWeak) / (ThresholdStrong - ThresholdWeak),0)
            #filtchunk_normalised_power = np.power(filtchunk_normalised,Parameters['WEIGHT_POWER'])
            
            print 'plotting figure now'
            
            plt.suptitle('%s samples'%(interestpoint), fontsize=10, fontweight='bold')
            plt.subplots_adjust(hspace = 0.5)
            #plt.subplots_adjust(hspace = 0.25,left= 0.12, bottom = 0.10, right = 0.90, top = 0.90, wspace = 0.2)
            
            #Raw data
            dataxis = fig1.add_subplot(gs[0,0:total_width])
            dataxis.set_title('DatChunks',fontsize=10)
            imdat = dataxis.imshow(np.transpose(chunk_raw[sampmin:sampmax,:]),interpolation="nearest",aspect="auto")
            #dataxis.set_xlabel('Samples')
            dataxis.set_ylabel('Channels')

            
           
            #Filtered data
            filaxis = fig1.add_subplot(gs[1,0:total_width])
            filaxis.set_title('FilteredChunks',fontsize=10)
            imfil = filaxis.imshow(np.transpose(chunk_fil[sampmin:sampmax,:]),interpolation="nearest",aspect="auto")
            #filaxis.set_xlabel('Samples')
            filaxis.set_ylabel('Channels')
            
            
           
            #Connected components
            compaxis = fig1.add_subplot(gs[2,0:total_width])
            compaxis.set_title('Threshold Crossings',fontsize=10)
            imcomp = compaxis.imshow(np.transpose(chunk_threshold.weak[sampmin:sampmax,:].astype(int)+chunk_threshold.strong[sampmin:sampmax,:].astype(int)),interpolation="nearest",aspect="auto")
            #compaxis.set_xlabel('Samples')
            compaxis.set_ylabel('Channels')
            for spiketimedebug in debugnextbits:
                compaxis.axvline(spiketimedebug[1]-sampmin,color = 'w') #plot a vertical line for s_fpeak
                print spiketimedebug[1]-sampmin
            
            conaxis = fig1.add_subplot(gs[3,0:total_width])
            conaxis.set_title('Connected Components',fontsize=10)
            imcon = conaxis.imshow(np.transpose(connected_comp_enum[sampmin:sampmax,:]),interpolation="nearest",aspect="auto");#plt.colorbar(imcon);
            conaxis.set_xlabel('Samples')
            conaxis.set_ylabel('Channels')
            for spiketimedebug in debugnextbits:
                conaxis.axvline(spiketimedebug[1]-sampmin,color = 'w') #plot a vertical line for s_fpeak
                print spiketimedebug[1]-sampmin
            
            ##offset = 2*np.amax(np.absolute(chunk_raw[sampmin:sampmax,:]))
            #offset = 2*np.amax(chunk_raw[sampmin:sampmax,:])
            #gain = 1
            ##rawdataxis = fig1.add_subplot(6,1,5)
            #rawdataxis = fig1.add_subplot(gs[4:7,0:total_width])
            #rawdataxis.set_title('Raw data',fontsize=10)
            #rawdataxis.hold(True)
            #for i in np.arange(prm['nchannels']):
                #rawdataxis.plot(gain*chunk_raw[sampmin:sampmax,i]+(prm['nchannels']-i)*offset)
            #for spiketimedebug in debugnextbits:
                #rawdataxis.axvline(spiketimedebug[1]-sampmin,color = 'k') #plot a vertical line for s_fpeak
            
            ##offsetfil = 2*np.amax(np.absolute(chunk_fil[sampmin:sampmax,:]))
            #offsetfil = 2*np.amax(chunk_fil[sampmin:sampmax,:])
            #gain_fil = 1
            ##fildataxis = fig1.add_subplot(6,1,6)
            #fildataxis = fig1.add_subplot(gs[8:11,0:total_width])
            #fildataxis.set_title('Filtered data',fontsize=10)
            #fildataxis.hold(True)
            #for i in np.arange(prm['nchannels']):
                #fildataxis.plot(gain_fil*chunk_fil[sampmin:sampmax,i]+(prm['nchannels']-i)*offsetfil)
            #for spiketimedebug in debugnextbits:
                #fildataxis.axvline(spiketimedebug[1]-sampmin,color = 'k') #plot a vertical line for s_fpeak    
           
            #Set this variable to True, if you want to see and adjust each plot in matplotlib as they arise.
            if prm['show_plots_as_they_arise']:
                plt.show()
            
            fig1.savefig('Debug_SD2floodfillchunk_%s_samples'%(interestpoint))
            
            if prm['save_graph_data']:
                tosave = [waveslist,debugnextbits,interestpoint,chunk_threshold, waveslist,chunk_fil,chunk_raw,connected_comp_enum,sampmin,sampmax,prm]
                with open('savegraphdata_%s.p'%(interestpoint),'wb') as f:
                    pickle.dump(tosave,f)
            #pickle.dump(tosave,open('savegraphdata_%s.p'%(interestpoint),'wb'))
